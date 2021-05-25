## import standard libraries
import typing
import pandas as pd
from typing import List
## import local files
from Request import Request
from interfaces.MySQLInterface import SQL
from schemas.Schema import Schema

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
    def __init__(self, game_id, column_names: List[str], session_ids, max_level, min_level):
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
        # lastly, get max and min levels, and get the session ids.
        self.max_level:            int = max_level
        self.min_level:            int = min_level
        self.session_ids:          List[int] = session_ids
        # utils.Logger.toStdOut("session_ids: " + str(session_ids), logging.DEBUG)
    
    @staticmethod
    def FromDB(db, settings, request: Request):
        db_settings = settings["db_config"]
        # TODO: Currently, this is retrieved separately from the schema. We may just want to load in one place, and check for a match or something.
        query = f"SHOW COLUMNS from {db_settings['DB_NAME_DATA']}.{db_settings['TABLE']}"
        db_cursor = db.cursor()
        col_names = SQL.Query(cursor=db_cursor, query=query)
        if request.GetGameID() == 'LAKELAND':
            lakeland_config = Schema('LAKELAND')['config']
            min_level = 0
            max_level = lakeland_config["MAX_SESSION_SECONDS"] // lakeland_config['WINDOW_SIZE_SECONDS']
        else:
            max_min_raw = SQL.SELECT(cursor=db_cursor, db_name=db_settings["DB_NAME_DATA"], table=db_settings["TABLE"],
                                     columns=["MAX(level)", "MIN(level)"], filter=f"`app_id`='{request.GetGameID()}'",
                                     distinct=True)
            max_level = max_min_raw[0][0]
            min_level = max_min_raw[0][1]
        sess_ids = request.RetrieveSessionIDs()
        return TableSchema(game_id=request.GetGameID(), column_names=[str(col) for col in col_names], session_ids=sess_ids, max_level=max_level, min_level=min_level)

    @staticmethod
    def FromCSV(data_frame: pd.DataFrame):
        col_names = list(data_frame.columns)
        game_id = data_frame['app_id'][0]
        sess_ids = list(data_frame['session_id'].unique())
        min_level = data_frame['level'].min()
        max_level = data_frame['level'].max()
        return TableSchema(game_id=game_id, column_names=col_names, session_ids=sess_ids, max_level=max_level, min_level=min_level)

    ## Simple utility function to turn a raw row from the file/database into a dictionary,
    #  indexed with the column names retrieved from the file/database.
    def RowToDict(self, row):
        return {self.column_names[i]: row[i] for i in range(len(self.column_names))}