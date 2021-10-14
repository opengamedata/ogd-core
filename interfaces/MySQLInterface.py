# global imports
from mysql.connector import connect, connection, cursor
import logging
import sshtunnel
import traceback
from datetime import datetime
from itertools import chain
from typing import Any, Dict, List, Set, Tuple, Union
# local imports
from DataInterface import DataInterface
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
    # Function to set up a connection to a database, via an ssh tunnel if available.
    @staticmethod
    def ConnectDB(db_settings:Dict[str,Any], ssh_settings:Union[Dict[str,Any],None]=None) -> Tuple[Union[sshtunnel.SSHTunnelForwarder,None], Union[connection.MySQLConnection,None]]:
        """
        Function to set up a connection to a database, via an ssh tunnel if available.

        :param db_settings: A dictionary mapping names of database parameters to values.
        :type db_settings: Dict[str,Any]
        :param ssh_settings: A dictionary mapping names of ssh parameters to values, or None if no ssh connection is desired., defaults to None
        :type ssh_settings: Union[Dict[str,Any],None], optional
        :return: A tuple consisting of the tunnel and database connection, respectively.
        :rtype: Tuple[Union[sshtunnel.SSHTunnelForwarder,None], Union[connection.MySQLConnection,None]]
        """
        tunnel  : Union[sshtunnel.SSHTunnelForwarder,None] = None
        db_conn : Union[connection.MySQLConnection,None]   = None
        # Load settings, set up consts.
        DB_NAME = db_settings["DB_NAME"]
        DB_USER = db_settings['DB_USER']
        DB_PW = db_settings['DB_PW']
        DB_HOST = db_settings['DB_HOST']
        DB_PORT = int(db_settings['DB_PORT'])
        sql_login = SQLLogin(host=DB_HOST, port=DB_PORT, user=DB_USER, pword=DB_PW, db_name=DB_NAME)
        Logger.toStdOut("Preparing database connection...", logging.INFO)
        if ssh_settings is not None:
            SSH_USER = ssh_settings['SSH_USER']
            SSH_PW = ssh_settings['SSH_PW']
            SSH_HOST = ssh_settings['SSH_HOST']
            SSH_PORT = ssh_settings['SSH_PORT']
            if (SSH_HOST != "" and SSH_USER != "" and SSH_PW != ""):
                ssh_login = SSHLogin(host=SSH_HOST, port=SSH_PORT, user=SSH_USER, pword=SSH_PW)
                tunnel,db_conn = SQL._connectToMySQLviaSSH(sql=sql_login, ssh=ssh_login)
        else:
            db_conn = SQL._connectToMySQL(login=sql_login)
            tunnel = None
        Logger.toStdOut("Done preparing database connection.", logging.INFO)
        return (tunnel, db_conn)

    # Function to help connect to a mySQL server.
    @staticmethod
    def _connectToMySQL(login: SQLLogin) -> Union[connection.MySQLConnection, None]:
        """Function to help connect to a mySQL server.

        Simply tries to make a connection, and prints an error in case of failure.
        :param login: A SQLLogin object with the data needed to log into MySQL.
        :type login: SQLLogin
        :return: If successful, a MySQLConnection object, otherwise None.
        :rtype: Union[connection.MySQLConnection, None]
        """
        try:
            db_conn = connection.MySQLConnection(host     = login.host,    port    = login.port,
                                                 user     = login.user,    password= login.pword,
                                                 database = login.db_name, charset = 'utf8')
            Logger.toStdOut(f"Connected to SQL (no SSH) at {login.host}:{login.port}/{login.db_name}, {login.user}", logging.INFO)
            return db_conn
        #except MySQLdb.connections.Error as err:
        except Exception as err:
            msg = f"""Could not connect to the MySql database.
            Login info: host={login.host}, port={login.port} w/type={type(login.port)}, db={login.db_name}, user={login.user}.
            Full error: {type(err)} {str(err)}"""
            Logger.Log(msg, logging.ERROR)
            traceback.print_tb(err.__traceback__)
            return None

    ## Function to help connect to a mySQL server over SSH.
    @staticmethod
    def _connectToMySQLviaSSH(sql: SQLLogin, ssh: SSHLogin) -> Tuple[Union[sshtunnel.SSHTunnelForwarder,None], Union[connection.MySQLConnection,None]]:
        """Function to help connect to a mySQL server over SSH.

        Simply tries to make a connection, and prints an error in case of failure.
        :param sql: A SQLLogin object with the data needed to log into MySQL.
        :type sql: SQLLogin
        :param ssh: An SSHLogin object with the data needed to log into MySQL.
        :type ssh: SSHLogin
        :return: An open connection to the database if successful, otherwise None.
        :rtype: Tuple[Union[sshtunnel.SSHTunnelForwarder,None], Union[connection.MySQLConnection,None]]
        """
        tunnel : Union[sshtunnel.SSHTunnelForwarder, None] = None
        db_conn   : Union[connection.MySQLConnection, None] = None
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
        if connected_ssh == True and tunnel is not None:
            # Then, connect to MySQL
            try:
                db_conn = connection.MySQLConnection(host     = sql.host,    port    = tunnel.local_bind_port,
                                                     user     = sql.user,    password= sql.pword,
                                                     database = sql.db_name, charset ='utf8')
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
    def disconnectMySQL(db:Union[connection.MySQLConnection,None], tunnel:Union[sshtunnel.SSHTunnelForwarder,None]=None) -> None:
        if db is not None:
            db.close()
            Logger.toStdOut("Closed database connection", logging.INFO)
        else:
            Logger.toStdOut("No db to close.", logging.DEBUG)
        if tunnel is not None:
            tunnel.stop()
            Logger.toStdOut("Stopped tunnel connection", logging.INFO)
        else:
            Logger.toStdOut("No tunnel to stop", logging.DEBUG)


    # Function to build and execute SELECT statements on a database connection.
    # @staticmethod
    # def INSERT(cursor:cursor.MySQLCursor,    db_name:str,                  table:str,
    #            columns:List[str],            items:List[Dict[str,object]], fetch_results:bool = False) -> Union[List[Tuple],None]:
    #     """Function to build and execute INSERT statements on a database connection.
    #     Assumes 

    #     :param cursor: A database cursor, retrieved from the active connection.
    #     :type cursor: cursor.MySQLCursor
    #     :param db_name: The name of the database to which we are connected.
    #     :type db_name: str
    #     :param table: The name of the table from which we want to make a selection.
    #     :type table: str
    #     :param columns: A list of columns whose values should be included in the insert. Only columns in this list will be included from the items.
    #     :type columns: List[str]
    #     :param items: A list of items to be inserted.
    #      Each item maps column names to values for insertion, and is converted to a "value" (SQL's term), a comma-separated list of values.
    #     :type items: List[Dict[str,object]]
    #     :param fetch_results: A bool to determine whether all results should be fetched and returned, defaults to True
    #     :type fetch_results: bool, optional
    #     :return: A collection of all rows from the selection, if fetch_results is true, otherwise None.
    #     :rtype: Union[List[Tuple],None]
    #     """
    #     table_path: str      = db_name + "." + str(table)
    #     values    : List[str] = []
    #     for item in items:
    #         val_list = ",".join([f"'{json.dumps(item[col])}'" for col in columns])
    #         values.append(f"({val_list})")

    #     ins_clause  = f"INSERT INTO {table_path}"
    #     cols_clause = f"({','.join(columns)})"
    #     vals_clause = f"VALUES {','.join(values)}"
    #     query = f"{ins_clause} {cols_clause} {vals_clause};"
    #     print(f"Insert query: {query}")
    #     return SQL.Query(cursor=cursor, query=query, fetch_results=fetch_results)

    # Function to build and execute SELECT statements on a database connection.
    @staticmethod
    def SELECT(cursor        :cursor.MySQLCursor, db_name       :str,         table         :str,
               columns       :List[str] = None,   filter        :str = None,
               sort_columns  :List[str] = None,   sort_direction:str = "ASC", grouping      :str = None,
               distinct      :bool      = False,  offset        :int = 0,     limit         :int = -1,
               fetch_results :bool      = True) -> Union[List[Tuple],None]:
        """Function to build and execute SELECT statements on a database connection.

        :param cursor: A database cursor, retrieved from the active connection.
        :type cursor: cursor.MySQLCursor
        :param db_name: The name of the database to which we are connected.
        :type db_name: str
        :param table: The name of the table from which we want to make a selection.
        :type table: str
        :param columns: A list of columns to be selected. If empty (or None), all columns will be used (SELECT * FROM ...). Defaults to None
        :type columns: List[str], optional
        :param filter: A string giving the constraints for a WHERE clause (The "WHERE" term itself should not be part of the filter string), defaults to None
        :type filter: str, optional
        :param sort_columns: A list of columns to sort results on. The order of columns in the list is the order given to SQL. Defaults to None
        :type sort_columns: List[str], optional
        :param sort_direction: The "direction" of sorting, either ascending or descending., defaults to "ASC"
        :type sort_direction: str, optional
        :param grouping: A column name to group results on. Subject to SQL rules for grouping, defaults to None
        :type grouping: str, optional
        :param distinct: A bool to determine whether to select only rows with distinct values in the column, defaults to False
        :type distinct: bool, optional
        :param limit: The maximum number of rows to be selected. Use -1 for no limit., defaults to -1
        :type limit: int, optional
        :param fetch_results: A bool to determine whether all results should be fetched and returned, defaults to True
        :type fetch_results: bool, optional
        :return: A collection of all rows from the selection, if fetch_results is true, otherwise None.
        :rtype: Union[List[Tuple],None]
        """
        d          = "DISTINCT" if distinct else ""
        cols = ",".join(columns) if columns is not None and len(columns) > 0 else "*"
        sort_cols  = ",".join(sort_columns) if sort_columns is not None and len(sort_columns) > 0 else None
        table_path = db_name + "." + str(table)
        params = []

        sel_clause = f"SELECT {d} {cols} FROM {table_path}"
        where_clause = "" if filter    is None else f"WHERE {filter}"
        group_clause = "" if grouping  is None else f"GROUP BY {grouping}"
        sort_clause  = "" if sort_cols is None else f"ORDER BY {sort_cols} {sort_direction} "
        lim_clause   = "" if limit < 0         else f"LIMIT {str(max(offset, 0))}, {str(limit)}" # don't use a negative for offset
        query = f"{sel_clause} {where_clause} {group_clause} {sort_clause} {lim_clause};"
        return SQL.Query(cursor=cursor, query=query, params=None, fetch_results=fetch_results)

    @staticmethod
    def Query(cursor:cursor.MySQLCursor, query:str, params:Union[Tuple,None], fetch_results: bool = True) -> Union[List[Tuple], None]:
        result : Union[List[Tuple], None] = None
        # first, we do the query.
        Logger.toStdOut(f"Running query: {query}\nWith params: {params}", logging.DEBUG)
        start = datetime.now()
        cursor.execute(query, params)
        time_delta = datetime.now()-start
        Logger.toStdOut(f"Query execution completed, time to execute: {time_delta}", logging.DEBUG)
        # second, we get the results.
        if fetch_results:
            result = cursor.fetchall()
            time_delta = datetime.now()-start
            Logger.toStdOut(f"Query fetch completed, total query time:    {time_delta} to get {len(result) if result is not None else 0:d} rows", logging.DEBUG)
        return result

class MySQLInterface(DataInterface):
    def __init__(self, game_id:str, settings):
        # set up data from params
        super().__init__(game_id=game_id)
        self._settings = settings
        # set up connection vars and try to make connection off the bat.
        self._tunnel : Union[sshtunnel.SSHTunnelForwarder, None] = None
        self._db : Union[connection.MySQLConnection, None] = None
        self._db_cursor : Union[cursor.MySQLCursor, None] = None
        self.Open()
        
    def _open(self, force_reopen:bool = False) -> bool:
        if force_reopen:
            self.Close()
            self.Open(force_reopen=False)
        if not self._is_open:
            start = datetime.now()
            self._tunnel, self._db = SQL.ConnectDB(db_settings=self._settings["MYSQL_CONFIG"], ssh_settings=self._settings["SSH_CONFIG"])
            if self._tunnel != None and self._db != None:
                self._db_cursor = self._db.cursor()
                self._is_open = True
                time_delta = datetime.now() - start
                Logger.Log(f"Database Connection Time: {time_delta}", logging.INFO)
                return True
            else:
                Logger.Log(f"Unable to open MySQL interface.", logging.ERROR)
                SQL.disconnectMySQL(tunnel=self._tunnel, db=self._db)
                return False
        else:
            return True

    def _close(self) -> bool:
        SQL.disconnectMySQL(tunnel=self._tunnel, db=self._db)
        Logger.toStdOut("Closed connection to MySQL.", logging.DEBUG)
        self._is_open = False
        return True

    def _rowsFromIDs(self, id_list: List[str], versions: Union[List[int],None]=None) -> List[Tuple]:
        ret_val = []
        # grab data for the given session range. Sort by event time, so
        if not self._db_cursor == None:
            if versions is not None and versions is not []:
                ver_filter = f" AND app_version in ({','.join([str(version) for version in versions])}) "
            else:
                ver_filter = ''
            # filt = f"app_id='{self._game_id}' AND (session_id  BETWEEN '{next_slice[0]}' AND '{next_slice[-1]}'){ver_filter}"
            id_list_string = ",".join([f"%s" for i in range(len(id_list))])
            db_name = self._settings["MYSQL_CONFIG"]["DB_NAME"]
            table_name = self._settings["MYSQL_CONFIG"]["TABLE"]
            filt = f"app_id=%s AND session_id IN ({id_list_string}){ver_filter}"
            query_string = f"SELECT * FROM {db_name}.{table_name} WHERE {filt} ORDER BY session_id, session_n ASC"
            params = [self._game_id] + [str(x) for x in id_list]
            data = SQL.Query(cursor=self._db_cursor, query=query_string, params=tuple(params), fetch_results=True)
            if data is not None:
                ret_val = data
            # self._select_queries.append(select_query) # this doesn't appear to be used???
        else:
            Logger.Log(f"Could not get data for {len(id_list)} sessions, MySQL connection is not open.", logging.WARN)
        return ret_val

    def _allIDs(self) -> List[str]:
        if not self._db_cursor == None:
            # filt = f"app_id='{self._game_id}' AND (session_id  BETWEEN '{next_slice[0]}' AND '{next_slice[-1]}'){ver_filter}"
            db_name = self._settings["MYSQL_CONFIG"]["DB_NAME"]
            table_name = self._settings["MYSQL_CONFIG"]["TABLE"]
            filt = f"`app_id`='{self._game_id}'"
            data = SQL.SELECT(cursor =self._db_cursor, db_name=db_name, table   =table_name,
                              columns=['session_id'],  filter =filt,    distinct=True)
            return [str(id[0]) for id in data] if data != None else []
            # self._select_queries.append(select_query) # this doesn't appear to be used???
        else:
            Logger.Log(f"Could not get list of all session ids, MySQL connection is not open.", logging.WARN)
            return []

    def _fullDateRange(self) -> Dict[str,datetime]:
        ret_val = {'min':datetime.now(), 'max':datetime.now()}
        if not self._db_cursor == None:
            # filt = f"app_id='{self._game_id}' AND (session_id  BETWEEN '{next_slice[0]}' AND '{next_slice[-1]}'){ver_filter}"
            db_name = self._settings["MYSQL_CONFIG"]["DB_NAME"]
            table_name = self._settings["MYSQL_CONFIG"]["TABLE"]
            # prep filter strings
            filt = f"`app_id`='{self._game_id}'"
            # run query
            result = SQL.SELECT(cursor=self._db_cursor, db_name=db_name, table=table_name,
                                columns=['MIN(server_time)', 'MAX(server_time)'], filter=filt)
            if result is not None:
                ret_val = {'min':result[0][0], 'max':result[0][1]}
        else:
            Logger.Log(f"Could not get full date range, MySQL connection is not open.", logging.WARN)
        return ret_val

    def _IDsFromDates(self, min:datetime, max:datetime, versions: Union[List[int],None]=None) -> List[str]:
        ret_val = []
        if not self._db_cursor == None:
            # alias long setting names.
            db_name = self._settings["MYSQL_CONFIG"]["DB_NAME"]
            table_name = self._settings["MYSQL_CONFIG"]["TABLE"]
            start = min.isoformat()
            end = max.isoformat()
            # prep filter strings
            ver_filter = f" AND `app_version` in ({','.join([str(x) for x in versions])}) " if versions else ''
            filt = f"`app_id`=\"{self._game_id}\" AND `session_n`='0' AND (`server_time` BETWEEN '{start}' AND '{end}'){ver_filter}"
            # run query
            # We grab the ids for all sessions that have 0th move in the proper date range.
            session_ids_raw = SQL.SELECT(cursor=self._db_cursor, db_name=db_name, table=table_name,
                                    columns=["`session_id`"], filter=filt,
                                    sort_columns=["`session_id`"], sort_direction="ASC", distinct=True)
            if session_ids_raw is not None:
                ret_val = [str(sess[0]) for sess in session_ids_raw]
        else:
            Logger.Log(f"Could not get session list for {min.isoformat()}-{max.isoformat()} range, MySQL connection is not open.", logging.WARN)
        return ret_val

    def _datesFromIDs(self, id_list:List[str], versions: Union[List[int],None]=None) -> Dict[str, datetime]:
        ret_val = {'min':datetime.now(), 'max':datetime.now()}
        if not self._db_cursor == None:
            # alias long setting names.
            db_name = self._settings["MYSQL_CONFIG"]["DB_NAME"]
            table_name = self._settings["MYSQL_CONFIG"]["TABLE"]
            # prep filter strings
            ids_string = ','.join([f"'{x}'" for x in id_list])
            ver_filter = f" AND `app_version` in ({','.join([str(x) for x in versions])}) " if versions else ''
            filt = f"`app_id`='{self._game_id}' AND `session_id` IN ({ids_string}){ver_filter}"
            # run query
            result = SQL.SELECT(cursor=self._db_cursor, db_name=db_name, table=table_name,
                                columns=['MIN(server_time)', 'MAX(server_time)'], filter=filt)
            if result is not None:
                ret_val = {'min':result[0][0], 'max':result[0][1]}
        else:
            Logger.Log(f"Could not get date range for {len(id_list)} sessions, MySQL connection is not open.", logging.WARN)
        return ret_val
