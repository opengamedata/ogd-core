# import libraries
from mysql.connector import connection, cursor
import logging
import sshtunnel
import traceback
from datetime import datetime
from typing import Any, Dict, List, Tuple, Optional
# import locals
from interfaces.DataInterface import DataInterface
from config.config import settings as default_settings
from schemas.IDMode import IDMode
from schemas.TableSchema import TableSchema
from utils import Logger


## Dumb struct to collect data used to establish a connection to a SQL database.
class SQLLogin:
    def __init__(self, host: str, port: int, db_name: str, user: str, pword: str):
        self.host    = host
        self.port    = port
        self.db_name = db_name
        self.user    = user
        self.pword   = pword
 
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
    def ConnectDB(db_settings:Dict[str,Any], ssh_settings:Optional[Dict[str,Any]]=None) -> Tuple[Optional[sshtunnel.SSHTunnelForwarder], Optional[connection.MySQLConnection]]:
        """
        Function to set up a connection to a database, via an ssh tunnel if available.

        :param db_settings: A dictionary mapping names of database parameters to values.
        :type db_settings: Dict[str,Any]
        :param ssh_settings: A dictionary mapping names of ssh parameters to values, or None if no ssh connection is desired., defaults to None
        :type ssh_settings: Optional[Dict[str,Any]], optional
        :return: A tuple consisting of the tunnel and database connection, respectively.
        :rtype: Tuple[Optional[sshtunnel.SSHTunnelForwarder], Optional[connection.MySQLConnection]]
        """
        tunnel  : Optional[sshtunnel.SSHTunnelForwarder] = None
        db_conn : Optional[connection.MySQLConnection]   = None
        # Load settings, set up consts.
        DB_HOST = db_settings['DB_HOST']
        DB_NAME = db_settings["DB_NAME"]
        DB_PORT = int(db_settings['DB_PORT'])
        DB_USER = db_settings['DB_USER']
        DB_PW = db_settings['DB_PW']
        sql_login = SQLLogin(host=DB_HOST, port=DB_PORT, db_name=DB_NAME, user=DB_USER, pword=DB_PW)
        Logger.Log("Preparing database connection...", logging.INFO)
        if ssh_settings is not None:
            SSH_USER = ssh_settings['SSH_USER']
            SSH_PW   = ssh_settings['SSH_PW']
            SSH_HOST = ssh_settings['SSH_HOST']
            SSH_PORT = ssh_settings['SSH_PORT']
            if (SSH_HOST != "" and SSH_USER != "" and SSH_PW != ""):
                ssh_login = SSHLogin(host=SSH_HOST, port=SSH_PORT, user=SSH_USER, pword=SSH_PW)
                tunnel,db_conn = SQL._connectToMySQLviaSSH(sql=sql_login, ssh=ssh_login)
            else:
                db_conn = SQL._connectToMySQL(login=sql_login)
                tunnel = None
        else:
            db_conn = SQL._connectToMySQL(login=sql_login)
            tunnel = None
        Logger.Log("Done preparing database connection.", logging.INFO)
        return (tunnel, db_conn)

    # Function to help connect to a mySQL server.
    @staticmethod
    def _connectToMySQL(login:SQLLogin) -> Optional[connection.MySQLConnection]:
        """Function to help connect to a mySQL server.

        Simply tries to make a connection, and prints an error in case of failure.
        :param login: A SQLLogin object with the data needed to log into MySQL.
        :type login: SQLLogin
        :return: If successful, a MySQLConnection object, otherwise None.
        :rtype: Optional[connection.MySQLConnection]
        """
        try:
            db_conn = connection.MySQLConnection(host     = login.host,    port    = login.port,
                                                 user     = login.user,    password= login.pword,
                                                 database = login.db_name, charset = 'utf8')
            Logger.Log(f"Connected to SQL (no SSH) at {login.host}:{login.port}/{login.db_name}, {login.user}", logging.DEBUG)
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
    def _connectToMySQLviaSSH(sql:SQLLogin, ssh:SSHLogin) -> Tuple[Optional[sshtunnel.SSHTunnelForwarder], Optional[connection.MySQLConnection]]:
        """Function to help connect to a mySQL server over SSH.

        Simply tries to make a connection, and prints an error in case of failure.
        :param sql: A SQLLogin object with the data needed to log into MySQL.
        :type sql: SQLLogin
        :param ssh: An SSHLogin object with the data needed to log into MySQL.
        :type ssh: SSHLogin
        :return: An open connection to the database if successful, otherwise None.
        :rtype: Tuple[Optional[sshtunnel.SSHTunnelForwarder], Optional[connection.MySQLConnection]]
        """
        tunnel    : Optional[sshtunnel.SSHTunnelForwarder] = None
        db_conn   : Optional[connection.MySQLConnection] = None
        MAX_TRIES : int = 5
        tries : int = 0
        connected_ssh : bool = False

        # First, connect to SSH
        while connected_ssh == False and tries < MAX_TRIES:
            if tries > 0:
                Logger.Log("Re-attempting to connect to SSH.", logging.INFO)
            try:
                tunnel = sshtunnel.SSHTunnelForwarder(
                    (ssh.host, ssh.port), ssh_username=ssh.user, ssh_password=ssh.pword,
                    remote_bind_address=(sql.host, sql.port), logger=Logger.std_logger
                )
                tunnel.start()
                connected_ssh = True
                Logger.Log(f"Connected to SSH at {ssh.host}:{ssh.port}, {ssh.user}", logging.DEBUG)
            except Exception as err:
                msg = f"Could not connect to the SSH: {type(err)} {str(err)}"
                Logger.Log(msg, logging.ERROR)
                Logger.Print(msg, logging.ERROR)
                traceback.print_tb(err.__traceback__)
                tries = tries + 1
        if connected_ssh == True and tunnel is not None:
            # Then, connect to MySQL
            try:
                db_conn = connection.MySQLConnection(host     = sql.host,    port    = tunnel.local_bind_port,
                                                     user     = sql.user,    password= sql.pword,
                                                     database = sql.db_name, charset ='utf8')
                Logger.Log(f"Connected to SQL (via SSH) at {sql.host}:{tunnel.local_bind_port}/{sql.db_name}, {sql.user}", logging.DEBUG)
                return (tunnel, db_conn)
            except Exception as err:
                msg = f"Could not connect to the MySql database: {type(err)} {str(err)}"
                Logger.Log(msg, logging.ERROR)
                Logger.Print(msg, logging.ERROR)
                traceback.print_tb(err.__traceback__)
                if tunnel is not None:
                    tunnel.stop()
                return (None, None)
        else:
            return (None, None)

    @staticmethod
    def disconnectMySQL(db:Optional[connection.MySQLConnection], tunnel:Optional[sshtunnel.SSHTunnelForwarder]=None) -> None:
        if db is not None:
            db.close()
            Logger.Log("Closed MySQL database connection", logging.DEBUG)
        else:
            Logger.Log("No MySQL database to close.", logging.DEBUG)
        if tunnel is not None:
            tunnel.stop()
            Logger.Log("Stopped MySQL tunnel connection", logging.DEBUG)
        else:
            Logger.Log("No MySQL tunnel to stop", logging.DEBUG)

    # Function to build and execute SELECT statements on a database connection.
    @staticmethod
    def SELECT(cursor        :cursor.MySQLCursor,          db_name        : str,                   table    : str,
               columns       :List[str]           = [],    filter         : Optional[str] = None,
               sort_columns  :Optional[List[str]] = None,  sort_direction : str           = "ASC", grouping : Optional[str] = None,
               distinct      :bool                = False, offset         : int           = 0,     limit    : int           = -1,
               fetch_results :bool                = True,  params         : Tuple[str]    = tuple()) -> Optional[List[Tuple]]:
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
        :rtype: Optional[List[Tuple]]
        """
        d          = "DISTINCT" if distinct else ""
        cols       = ",".join(columns) if columns is not None and len(columns) > 0 else "*"
        sort_cols  = ",".join(sort_columns) if sort_columns is not None and len(sort_columns) > 0 else None
        table_path = db_name + "." + str(table)

        sel_clause = f"SELECT {d} {cols} FROM {table_path}"
        where_clause = "" if filter    is None else f"WHERE {filter}"
        group_clause = "" if grouping  is None else f"GROUP BY {grouping}"
        sort_clause  = "" if sort_cols is None else f"ORDER BY {sort_cols} {sort_direction} "
        lim_clause   = "" if limit < 0         else f"LIMIT {str(max(offset, 0))}, {str(limit)}" # don't use a negative for offset
        query = f"{sel_clause} {where_clause} {group_clause} {sort_clause} {lim_clause};"
        return SQL.Query(cursor=cursor, query=query, params=params, fetch_results=fetch_results)

    @staticmethod
    def Query(cursor:cursor.MySQLCursor, query:str, params:Optional[Tuple], fetch_results: bool = True) -> Optional[List[Tuple]]:
        result : Optional[List[Tuple]] = None
        # first, we do the query.
        Logger.Log(f"Running query: {query}\nWith params: {params}", logging.DEBUG)
        start = datetime.now()
        cursor.execute(query, params)
        time_delta = datetime.now()-start
        Logger.Log(f"Query execution completed, time to execute: {time_delta}", logging.DEBUG)
        # second, we get the results.
        if fetch_results:
            result = cursor.fetchall()
            time_delta = datetime.now()-start
            Logger.Log(f"Query fetch completed, total query time:    {time_delta} to get {len(result) if result is not None else 0:d} rows", logging.DEBUG)
        return result

class MySQLInterface(DataInterface):

    # *** BUILT-INS ***

    def __init__(self, game_id:str, config:Dict[str,Any]):
        self._tunnel    : Optional[sshtunnel.SSHTunnelForwarder] = None
        self._db        : Optional[connection.MySQLConnection] = None
        self._db_cursor : Optional[cursor.MySQLCursor] = None
        super().__init__(game_id=game_id, config=config)
        self.Open()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _open(self, force_reopen:bool = False) -> bool:
        if force_reopen:
            self.Close()
            self.Open(force_reopen=False)
        if not self._is_open:
            start = datetime.now()
            default_source = default_settings["GAME_SOURCE_MAP"][self._game_id]["source"]

            _sql_cfg = self._config.get("source") or default_settings["GAME_SOURCES"][default_source]
            _ssh_cfg = default_settings["SSH_CONFIG"]
            self._tunnel, self._db = SQL.ConnectDB(db_settings=_sql_cfg, ssh_settings=_ssh_cfg)
            if self._db is not None:
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
        Logger.Log("Closed connection to MySQL.", logging.DEBUG)
        self._is_open = False
        return True

    def _loadTableSchema(self, game_id:str) -> TableSchema:
        _schema_name = self._config.get("schema") or default_settings['GAME_SOURCE_MAP'].get(game_id, {}).get('schema', "NO SCHEMA DEFINED")
        return TableSchema(schema_name=_schema_name)

    def _allIDs(self) -> List[str]:
        if not self._db_cursor == None:
            default_source = default_settings["GAME_SOURCE_MAP"][self._game_id]["source"]
            db_name    : str = self._config.get("source", {}).get("DB_NAME") or default_settings[default_source]["DB_NAME"]
            table_name : str = self._config.get("table") or default_settings["GAME_SOURCE_MAP"][self._game_id].get("table", "TABLE_NAME_NOT_FOUND")

            filt   = None
            params = tuple()
            if table_name != self._game_id:
                filt = f"`app_id`=%s"
                params = tuple(self._game_id)
            data = SQL.SELECT(cursor =self._db_cursor, db_name=db_name, table   =table_name,
                              columns=['session_id'],  filter =filt,    distinct=True,
                              params =params)
            return [str(id[0]) for id in data] if data != None else []
        else:
            Logger.Log(f"Could not get list of all session ids, MySQL connection is not open.", logging.WARN)
            return []

    def _fullDateRange(self) -> Dict[str,datetime]:
        ret_val = {'min':datetime.now(), 'max':datetime.now()}
        if not self._db_cursor == None:
            default_source = default_settings["GAME_SOURCE_MAP"][self._game_id]["source"]

            db_name    : str = self._config.get("source", {}).get("DB_NAME") or default_settings[default_source]["DB_NAME"]
            table_name : str = self._config.get("table") or default_settings["GAME_SOURCE_MAP"][self._game_id].get("table", "TABLE_NAME_NOT_FOUND")
            # prep filter strings
            filt   = None
            params = tuple()
            if table_name != self._game_id:
                filt = f"`app_id`=%s"
                params = tuple(self._game_id)
            # run query
            result = SQL.SELECT(cursor=self._db_cursor, db_name=db_name, table=table_name,
                                columns=['MIN(server_time)', 'MAX(server_time)'], filter=filt,
                                params =params)
            if result is not None:
                ret_val = {'min':result[0][0], 'max':result[0][1]}
        else:
            Logger.Log(f"Could not get full date range, MySQL connection is not open.", logging.WARN)
        return ret_val

    def _rowsFromIDs(self, id_list:List[str], id_mode:IDMode=IDMode.SESSION, versions:Optional[List[int]]=None) -> List[Tuple]:
        ret_val = []
        # grab data for the given session range. Sort by event time, so
        if not self._db_cursor == None:
            # filt = f"app_id='{self._game_id}' AND (session_id  BETWEEN '{next_slice[0]}' AND '{next_slice[-1]}'){ver_filter}"
            default_source = default_settings["GAME_SOURCE_MAP"][self._game_id]["source"]

            db_name    : str = self._config.get("source", {}).get("DB_NAME") or default_settings[default_source]["DB_NAME"]
            table_name : str = self._config.get("table") or default_settings["GAME_SOURCE_MAP"][self._game_id].get("table", "TABLE_NAME_NOT_FOUND")

            filters = []
            params = tuple()
            if table_name != self._game_id:
                filters.append(f"`app_id`=%s")
                params = tuple(self._game_id)

            # if versions is not None and versions is not []:
            #     filters.append(f"app_version in ({','.join([str(version) for version in versions])})")

            id_list_string = ",".join([f"%s" for i in range(len(id_list))])
            if id_mode == IDMode.SESSION:
                filters.append(f"`session_id` IN ({id_list_string})")
            elif id_mode == IDMode.USER:
                filters.append(f"`player_id` IN ({id_list_string})")
            else:
                raise ValueError("Invalid IDMode in MySQLInterface!")

            filter_clause = " AND ".join(filters)
            # sess_id_column = str(self._TableSchema._column_map.SessionID)
            sess_index_column = str(self._TableSchema._column_map.EventSequenceIndex)
            query_string = f"SELECT * FROM {db_name}.{table_name} WHERE {filter_clause} ORDER BY `session_id`, `{sess_index_column}` ASC"
            params = [self._game_id] + [str(x) for x in id_list] if table_name != self._game_id else [str(x) for x in id_list]
            data = SQL.Query(cursor=self._db_cursor, query=query_string, params=tuple(params), fetch_results=True)
            if data is not None:
                ret_val = data
            # self._select_queries.append(select_query) # this doesn't appear to be used???
        else:
            Logger.Log(f"Could not get data for {len(id_list)} sessions, MySQL connection is not open.", logging.WARN)
        return ret_val

    def _IDsFromDates(self, min:datetime, max:datetime, versions:Optional[List[int]]=None) -> List[str]:
        ret_val = []
        if not self._db_cursor == None:
            # alias long setting names.
            default_source = default_settings["GAME_SOURCE_MAP"][self._game_id]["source"]
            db_name    : str = self._config.get("source", {}).get("DB_NAME") or default_settings[default_source]["DB_NAME"]
            table_name : str = self._config.get("table") or default_settings["GAME_SOURCE_MAP"][self._game_id].get("table", "TABLE_NAME_NOT_FOUND")
            # prep filter strings
            filters = []
            params = tuple()
            if table_name != self._game_id:
                filters.append(f"`app_id`=%s")
                params = tuple(self._game_id)

            # if versions is not None and versions is not []:
            #     filters.append(f"app_version in ({','.join([str(version) for version in versions])})")
            sess_index_column = str(self._TableSchema._column_map.EventSequenceIndex)
            filters.append(f"`{sess_index_column}`='0'")
            filters.append(f"(`server_time` BETWEEN '{min.isoformat()}' AND '{max.isoformat()}')")
            filter_clause = " AND ".join(filters)
            # run query
            # We grab the ids for all sessions that have 0th move in the proper date range.
            session_ids_raw = SQL.SELECT(cursor=self._db_cursor, db_name=db_name, table=table_name,
                                    columns=["`session_id`"], filter=filter_clause,
                                    sort_columns=["`session_id`"], sort_direction="ASC", distinct=True)
            if session_ids_raw is not None:
                ret_val = [str(sess[0]) for sess in session_ids_raw]
        else:
            Logger.Log(f"Could not get session list for {min.isoformat()}-{max.isoformat()} range, MySQL connection is not open.", logging.WARN)
        return ret_val

    def _datesFromIDs(self, id_list:List[str], id_mode:IDMode=IDMode.SESSION, versions:Optional[List[int]]=None) -> Dict[str, datetime]:
        ret_val = {'min':datetime.now(), 'max':datetime.now()}
        if not self._db_cursor == None:
            # alias long setting names.
            default_source = default_settings["GAME_SOURCE_MAP"][self._game_id]["source"]

            db_name    : str = self._config.get("source", {}).get("DB_NAME") or default_settings[default_source]["DB_NAME"]
            table_name : str = self._config.get("table") or default_settings["GAME_SOURCE_MAP"][self._game_id].get("table", "TABLE_NAME_NOT_FOUND")
            # prep filter strings
            # TODO: Need to fix these as well to support general usage.
            ids_string = ','.join([f"'{x}'" for x in id_list])
            app_filter = f"`app_id`=\"{self._game_id}\" AND" if table_name != self._game_id else ""
            ver_filter = f" AND `app_version` in ({','.join([str(x) for x in versions])}) " if versions else ''
            if id_mode == IDMode.SESSION:
                filt = f"{app_filter} `session_id` IN ({ids_string}){ver_filter}"
            elif id_mode == IDMode.USER:
                filt = f"{app_filter} `player_id` IN ({ids_string}){ver_filter}"
            else:
                raise ValueError("Invalid IDMode in MySQLInterface!")
            # run query
            result = SQL.SELECT(cursor=self._db_cursor, db_name=db_name, table=table_name,
                                columns=['MIN(server_time)', 'MAX(server_time)'], filter=filt)
            if result is not None:
                ret_val = {'min':result[0][0], 'max':result[0][1]}
        else:
            Logger.Log(f"Could not get date range for {len(id_list)} sessions, MySQL connection is not open.", logging.WARN)
        return ret_val

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
