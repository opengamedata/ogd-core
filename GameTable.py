## import standard libraries
import typing
## import local files
import Request
import utils

## Dumb struct to hold info about the structure of database data for a particular game.
## Just here to help keep useful data together for easier passing around.
class GameTable:
    def __init__(self, db, settings, request: Request):
        ## Define instance vars
        self.column_names:       typing.List[str]
        self.complex_data_index: int
        self.client_time_index:  int
        self.session_id_index:   int
        self.event_index:        int
        self.level_index:        int
        self.max_level:          int
        self.min_level:          int
        self.session_ids:        typing.List[int]
        ## Set instance vars
        db_cursor = db.cursor(buffered=True)
        self.column_names = GameTable._getColumnNames(db_cursor, db, settings)
        ## Take note of specific indices which will be useful when using a GameTable
        self.complex_data_index = self.column_names.index("event_data_complex")
        self.client_time_index = self.column_names.index("client_time")
        self.session_id_index = self.column_names.index("session_id")
        self.event_index = self.column_names.index("event")
        self.level_index = self.column_names.index("level")
        max_min_raw = utils.SQL.SELECT(cursor=db_cursor, db_name=db.database, table=settings["table"],
                                        columns=["MAX(level)", "MIN(level)"], filter="app_id=\"{}\"".format(request.game_id),
                                        distinct=True)
        self.max_level = max_min_raw[0][0]
        self.min_level = max_min_raw[0][1]
        self.session_ids = GameTable._getSessionIDs(db_cursor, db, settings, request)
        # logging.debug("session_ids: " + str(session_ids))
    
    @staticmethod
    def _getColumnNames(db_cursor, db, settings):
        db_cursor.execute("SHOW COLUMNS from {}.{}".format(db.database, settings["table"]))
        return [col[0] for col in db_cursor.fetchall()]
    
    @staticmethod
    def _getSessionIDs(db_cursor, db, settings, request):
        ## We grab the ids for all sessions that have 0th move in the proper date range.
        filt = "app_id=\"{}\" AND session_n=0 AND (server_time BETWEEN '{}' AND '{}')".format( \
                    request.game_id, request.start_date.isoformat(), request.end_date.isoformat())
        session_ids_raw = utils.SQL.SELECT(cursor=db_cursor, db_name=db.database, table=settings["table"],
                                        columns=["session_id"], filter=filt,
                                        sort_columns=["session_id"], sort_direction="ASC", distinct=True, limit=request.max_sessions)
        return [sess[0] for sess in session_ids_raw]