# global imports
import http
import logging
import math
import sshtunnel
import traceback
from datetime import datetime
from MySQLdb import connect, connections, cursors
from typing import Any, Dict, List, Tuple, Union
# local imports
from interfaces.DataInterface import DataInterface
from schemas.Schema import Schema
from utils import Logger


## Dumb struct to collect data used to establish a connection to a SQL database.
class SQLLogin:
    def __init__(self, host: str, port: int, user: str, pword: str, db_name: str):
        self.host    = host
        self.port    = port
        self.user    = user
        self.pword   = pword
        self.db_name = db_name

## Dumb struct to collect data used to establish a connection over ssh.
class SSHLogin:
    def __init__(self, host: str, port: int, user: str, pword: str):
        self.host    = host
        self.port    = port
        self.user    = user
        self.pword   = pword

## @class SQL
#  A utility class containing some functions to assist in retrieving from a database.
#  Specifically, helps to connect to a database, make selections, and provides
#  a nicely formatted 500 error message.
class SQL:
    ## Function to set up a connection to a database, via an ssh tunnel if available.
    #  @return A tuple consisting of the tunnel and database connection, respectively.
    @staticmethod
    def prepareDB(db_settings:Dict[str,Any], ssh_settings:Dict[str,Any]) -> Tuple[Union[sshtunnel.SSHTunnelForwarder,None], Union[connections.Connection,None]]:
        # Load settings, set up consts.
        DB_NAME_DATA = db_settings["DB_NAME_DATA"]
        DB_USER = db_settings['DB_USER']
        DB_PW = db_settings['DB_PW']
        DB_HOST = db_settings['DB_HOST']
        DB_PORT = db_settings['DB_PORT']
        SSH_USER = ssh_settings['SSH_USER']
        SSH_PW = ssh_settings['SSH_PW']
        SSH_HOST = ssh_settings['SSH_HOST']
        SSH_PORT = ssh_settings['SSH_PORT']

        # set up other global vars as needed:
        sql_login = SQLLogin(host=DB_HOST, port=DB_PORT, user=DB_USER, pword=DB_PW, db_name=DB_NAME_DATA)
        # Logger.toStdOut("We're preparing database.", logging.INFO)
        if (SSH_HOST != "" and SSH_USER != "" and SSH_PW != ""):
            # Logger.toStdOut(f"Setting up ssh host connection.", logging.INFO)
            ssh_login = SSHLogin(host=SSH_HOST, port=SSH_PORT, user=SSH_USER, pword=SSH_PW)
            tunnel,db_conn = SQL.connectToMySQLViaSSH(sql=sql_login, ssh=ssh_login)
        else:
            # Logger.toStdOut("Skipping SSH part of login.", logging.INFO)
            db_conn = SQL.connectToMySQL(login=sql_login)
            tunnel = None
        return (tunnel, db_conn)

    ## Function to help connect to a mySQL server.
    #  Simply tries to make a connection, and prints an error in case of failure.
    #
    #  @param host      The name of the database host server.
    #  @param port      The database server port to which we want to connect.
    #  @param user      Username for connecting to the database.
    #  @param password  The given user's password.
    #  @param database  The actual name of the database on the host.
    #  @return          An open connection to the database if successful,
    #                       otherwise None.
    @staticmethod
    def connectToMySQL(login: SQLLogin) -> Union[connections.Connection, None]:
        try:
            db_conn = connect(host = login.host, port = login.port,
                           user = login.user, password = login.pword,
                       database = login.db_name, charset='utf8')
            Logger.toStdOut(f"Connected to SQL (no SSH) at {login.host}:{login.port}/{login.db_name}, {login.user}", logging.INFO)
            return db_conn
        #except MySQLdb.connections.Error as err:
        except Exception as err:
            msg = f"Could not connect to the MySql database: {type(err)} {str(err)}"
            Logger.toStdOut(msg, logging.ERROR)
            Logger.toPrint(msg, logging.ERROR)
            traceback.print_tb(err.__traceback__)
            return None

    ## Function to help connect to a mySQL server over SSH.
    #  Simply tries to make a connection, and prints an error in case of failure.
    #
    #  @param host      The name of the database host server.
    #  @param port      The database server port to which we want to connect.
    #  @param user      Username for connecting to the database.
    #  @param password  The given user's password.
    #  @param database  The actual name of the database on the host.
    #  @return          An open connection to the database if successful,
    #                       otherwise None.
    @staticmethod
    def connectToMySQLViaSSH(sql: SQLLogin, ssh: SSHLogin) -> Tuple[Union[sshtunnel.SSHTunnelForwarder,None], Union[connections.Connection,None]]:
        tunnel : Union[sshtunnel.SSHTunnelForwarder, None] = None
        db_conn   : Union[connections.Connection, None] = None
        MAX_TRIES : int = 5
        tries : int = 0
        connected_ssh : bool = False

        # First, connect to SSH
        while connected_ssh == False and tries < MAX_TRIES:
            if tries > 0:
                Logger.toStdOut("Re-attempting to connect to SSH.", logging.INFO)
            try:
                tunnel = sshtunnel.SSHTunnelForwarder(
                    (ssh.host, ssh.port), ssh_username=ssh.user, ssh_password=ssh.pword,
                    remote_bind_address=(sql.host, sql.port), logger=Logger.std_logger
                )
                tunnel.start()
                connected_ssh = True
                Logger.toStdOut(f"Connected to SSH at {ssh.host}:{ssh.port}, {ssh.user}", logging.INFO)
            except Exception as err:
                msg = f"Could not connect to the SSH: {type(err)} {str(err)}"
                Logger.Log(msg, logging.ERROR)
                Logger.toPrint(msg, logging.ERROR)
                traceback.print_tb(err.__traceback__)
                tries = tries + 1
        if connected_ssh == True:
            # Then, connect to MySQL
            try:
                db_conn = connect(host = sql.host, port = tunnel.local_bind_port,
                               user = sql.user, password = sql.pword,
                           database = sql.db_name, charset='utf8')
                Logger.toStdOut(f"Connected to SQL (via SSH) at {sql.host}:{tunnel.local_bind_port}/{sql.db_name}, {sql.user}", logging.INFO)
                return (tunnel, db_conn)
            except Exception as err:
                msg = f"Could not connect to the MySql database: {type(err)} {str(err)}"
                Logger.Log(msg, logging.ERROR)
                Logger.toPrint(msg, logging.ERROR)
                traceback.print_tb(err.__traceback__)
                if tunnel is not None:
                    tunnel.stop()
                return (None, None)
        else:
            return (None, None)

    @staticmethod
    def disconnectMySQLViaSSH(tunnel:sshtunnel.SSHTunnelForwarder, db:connections.Connection) -> None:
        if db is not None:
            db.close()
            # Logger.toStdOut("Closed database connection", logging.INFO)
        else:
            Logger.toStdOut("No db to close.", logging.INFO)
        if tunnel is not None:
            tunnel.stop()
            # Logger.toStdOut("Stopped tunnel connection", logging.INFO)
        # else:
            # Logger.toStdOut("No tunnel to stop", logging.INFO)

    ## Function to build and execute SELECT statements on a database connection.
    #  @param cursor        A database cursor, retrieved from the active connection.
    #  @param db_name       The name of the database to which we are connected.
    #  @param table         The name of the table from which we want to make a selection.
    #  @param columns       A list of columns to be selected. If empty (or None),
    #                           all columns will be used (SELECT * FROM ...).
    #                           Default: None
    #  @param filter        A string giving the constraints for a WHERE clause.
    #                           (The "WHERE" term itself should not be part of the filter string)
    #                           Default: None
    #  @param limit         The maximum number of rows to be selected. Use -1 for no limit.
    #                           Default: -1
    #  @param sort_columns  A list of columns to sort results on. The order of columns
    #                           in the list is the order given to SQL
    #                           Default: None
    #  @param sort_direction The "direction" of sorting, either ascending or descending.
    #                           Default: "ASC"
    #  @param grouping      A column name to group results on. Subject to SQL rules for grouping.
    #                           Default: None
    #  @param distinct      A bool to determine whether to select only rows with
    #                           distinct values in the column.
    #                           Default: False
    #  @param distinct      A bool to determine whether all results should be fetched and returned.
    #                           Default: True
    #  @return              A collection of all rows from the selection, if fetch_results is true,
    #                           otherwise None.
    @staticmethod
    def SELECT(cursor      :cursors.Cursor,    db_name       :str,         table         :str,
               columns     :List[str] = None,  join          :str = None,  filter        :str = None,
               sort_columns:List[str] = None,  sort_direction:str = "ASC", grouping      :str = None,
               distinct    :bool      = False, limit         :int = -1,    fetch_results :bool = True) -> Union[List[Tuple],None]:
        query = SQL._prepareSelect(db_name=db_name, table=table, columns=columns, join=join, filter=filter, limit=limit,
                                   sort_columns=sort_columns, sort_direction=sort_direction, grouping=grouping,
                                   distinct=distinct)
        return SQL.SELECTfromQuery(cursor=cursor, query=query, fetch_results=fetch_results)

    @staticmethod
    def SELECTfromQuery(cursor:cursors.Cursor, query: str, fetch_results: bool = True) -> Union[List[Tuple], None]:
        result : Union[List[Tuple], None] = None
        # first, we do the query.
        Logger.toStdOut(f"Running query: {query}", logging.DEBUG)
        start = datetime.now()
        cursor.execute(query)
        time_delta = datetime.now()-start
        num_min = math.floor(time_delta.total_seconds()/60)
        num_sec = time_delta.total_seconds() % 60
        Logger.toStdOut(f"Query execution completed, time to execute: {num_min:d} min, {num_sec:.3f} sec", logging.DEBUG)
        # second, we get the results.
        if fetch_results:
            result = cursor.fetchall()
        time_delta = datetime.now()-start
        num_min = math.floor(time_delta.total_seconds()/60)
        num_sec = time_delta.total_seconds() % 60
        Logger.toStdOut(f"Query fetch completed, total query time:    {num_min:d} min, {num_sec:.3f} sec to get {len(result):d} rows", logging.DEBUG)
        return result

    @staticmethod
    def _prepareSelect(db_name: str, table:str, columns: List[str] = None, join: str = None, filter: str = None, limit: int = -1,
               sort_columns: List[str] = None, sort_direction = "ASC", grouping: str = None,
               distinct: bool = False):
        d = "DISTINCT " if distinct else ""
        cols      = ",".join(columns)      if columns is not None      and len(columns) > 0      else "*"
        sort_cols = ",".join(sort_columns) if sort_columns is not None and len(sort_columns) > 0 else None
        table_path = db_name + "." + str(table)

        sel_clause   = "SELECT " + d + cols + " FROM " + table_path
        join_clause  = "" if join      is None else f" {join}"
        where_clause = "" if filter    is None else f" WHERE {filter}"
        group_clause = "" if grouping  is None else f" GROUP BY {grouping}"
        sort_clause  = "" if sort_cols is None else f" ORDER BY {sort_cols} {sort_direction} "
        lim_clause   = "" if limit < 0         else f" LIMIT {str(limit)}"

        return sel_clause + join_clause + where_clause + group_clause + sort_clause + lim_clause + ";"

    @staticmethod
    def Query(cursor, query: str, fetch_results: bool = True) -> Union[List[Tuple], None]:
        Logger.toStdOut("Running query: " + query, logging.DEBUG)
        start = datetime.now()
        cursor.execute(query)
        Logger.toStdOut(f"Query execution completed, time to execute: {datetime.now()-start}", logging.DEBUG)
        return [col[0] for col in cursor.fetchall()] if fetch_results else None

    ## Simple function to construct and log a nice server 500 error message.
    #  @param err_msg A more detailed error message with info to help debugging.
    @staticmethod
    def server500Error(err_msg: str):
        val = http.HTTPStatus.INTERNAL_SERVER_ERROR.value
        phrase = http.HTTPStatus.INTERNAL_SERVER_ERROR.phrase
        Logger.toStdOut(f"HTTP Response: {val}{phrase}", logging.ERROR)
        Logger.toStdOut(f"Error Message: {err_msg}", logging.ERROR)

class MySQLInterface(DataInterface):
    def __init__(self, game_id:str, game_schema:Schema, settings):
        super().__init__(game_name=game_id)
        self._game_schema = game_schema
        self._settings = settings
        self._tunnel = None
        self._db = None
        self._db_cursor = None
        self.Open()
        
    @abc.abstractmethod
    def Open(self) -> bool:
        if not self._is_open:
            self._tunnel, self._db = SQL.prepareDB(db_settings=self._settings["db_config"], ssh_settings=self._settings["ssh_config"])
            self._db_cursor = self._db.cursor()

    @abc.abstractmethod
    def Close(self) -> bool:
        pass

    def _retrieveFromIDs(self, id_list: List[int]) -> List:
        # grab data for the given session range. Sort by event time, so
        if self._game_id == 'LAKELAND' or self._game_id == 'JOWILDER':
            ver_filter = f" AND app_version in ({','.join([str(x) for x in self._game_schema.schema()['config']['SUPPORTED_VERS']])}) "
        else:
            ver_filter = ''
        id_string = ','.join([f"'{x}'" for x in id_list])
        # filt = f"app_id='{self._game_id}' AND (session_id  BETWEEN '{next_slice[0]}' AND '{next_slice[-1]}'){ver_filter}"
        filt = f"app_id='{self._game_id}' AND session_id  IN ({id_string}){ver_filter}"
        query = SQL._prepareSelect(db_name=self._settings["db_config"]["DB_NAME_DATA"],
                                         table=self._settings["db_config"]["TABLE"], columns=None, filter=filt, limit=-1,
                                         sort_columns=["session_id", "session_n"], sort_direction="ASC",
                                         grouping=None, distinct=False)
        # self._select_queries.append(select_query) # this doesn't appear to be used???
        return SQL.SELECTfromQuery(cursor=self._db_cursor, query=query, fetch_results=True)

    @abc.abstractmethod
    def _IDsFromDates(self, min, max):
        pass

    @abc.abstractmethod
    def _datesFromIDs(self, ids:List[int]):
        pass