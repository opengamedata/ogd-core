## import standard libraries
import typing
import pandas as pd
from typing import List, Tuple, Union
from pandas.io.parsers import TextFileReader
## import local files
from interfaces.MySQLInterface import SQL
from schemas.GameSchema import GameSchema
from schemas.Event import Event

## @class TableSchema
#  Dumb struct to hold useful info about the structure of database data
#  for a particular game.
#  This includes the indices of several important database columns, the names
#  of the database columns, the max and min levels in the game, and a list of
#  IDs for the game sessions in the given requested date range.
class TableSchema:
    ## Constructor for the TableSchema class.
    #  Given a database connection and a game data request,
    #  this retrieves a bit of information from the database to fill in the
    #  class variables.
    #  @param db        A database connection to the table corresponding to this TableSchema.
    #  @param settings  The dictionary of settings for the app
    #  @param request   A request object, with information about a date range
    #                   and other information on what data to retrieve.
    def __init__(self, game_id, column_names: List[str], max_level, min_level):
        # Define instance vars
        self.game_id:      str              = game_id
        self.column_names: List[str] = column_names
        # Take note of specific indices which will be useful when using a TableSchema
        # TODO: Honestly, should just make a reverse index dictionary.
        self.app_version_index:    int = self.column_names.index("app_version")
        self.complex_data_index:   int = self.column_names.index("event_data_complex")
        self.remote_addr_index:    int = self.column_names.index("remote_addr")
        self.client_time_index:    int = self.column_names.index("client_time")
        self.session_id_index:     int = self.column_names.index("session_id")
        self.event_index:          int = self.column_names.index("event")
        self.level_index:          int = self.column_names.index("level")
        self.client_time_ms_index: int = self.column_names.index("client_time_ms")
        self.server_time_index:    int = self.column_names.index("server_time")
        self.pers_session_id_index:int = self.column_names.index("persistent_session_id")
        self.event_custom_index:   int = self.column_names.index("event_custom")
        self.version_index:        int = self.column_names.index("app_version")
        self.player_id_index:      int = self.column_names.index("player_id")
        # utils.Logger.toStdOut("session_ids: " + str(session_ids), logging.DEBUG)

    def RowToEvent(self, row: Tuple):
        row_dict = {self.column_names[i]: row[i] for i in range(len(self.column_names))}
        id     = row_dict['id']
        app_id = row_dict['app_id']
        app_id_fast = row_dict['app_id_fast']
        app_version = row_dict['app_version']
        session_id  = row_dict['session_id']
        persistent_session_id  = row_dict['persistent_session_id']
        player_id  = row_dict['player_id']
        level      = row_dict['level']
        event      = row_dict['event']
        event_custom       = row_dict['event_custom']
        event_data_simple  = row_dict['event_data_simple']
        event_data_complex = row_dict['event_data_complex']
        client_time     = row_dict['client_time']
        client_time_ms  = row_dict['client_time_ms']
        server_time     = row_dict['server_time']
        remote_addr     = row_dict['remote_addr']
        req_id          = row_dict['req_id']
        session_n       = row_dict['session_n']
        http_user_agent = row_dict['http_user_agent']
        return Event(id=id, app_id=app_id, app_id_fast=app_id_fast, app_version=app_version,
                     session_id=session_id, persistent_session_id=persistent_session_id,
                     player_id=player_id, level=level, event=event, event_custom=event_custom,
                     event_data_simple=event_data_simple, event_data_complex=event_data_complex,
                     client_time=client_time, client_time_ms=client_time_ms, server_time=server_time,
                     remote_addr=remote_addr, req_id=req_id, session_n=session_n, http_user_agent=http_user_agent)

    ## Simple utility function to turn a raw row from the file/database into a dictionary,
    #  indexed with the column names retrieved from the file/database.
    def RowToDict(self, row):
        return {self.column_names[i]: row[i] for i in range(len(self.column_names))}