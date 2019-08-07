## import standard libraries
import logging
import typing
from datetime import datetime
## import local files
import Request
import utils

## @class GameTable
#  Dumb struct to hold useful info about the structure of database data
#  for a particular game.
#  This includes the indices of several important database columns, the names
#  of the database columns, the max and min levels in the game, and a list of
#  IDs for the game sessions in the given requested date range.
class GameTable:
    ## Constructor for the GameTable class.
    #  Given a database connection and a game data request,
    #  this retrieves a bit of information from the database to fill in the
    #  class variables.
    #  @param db        A database connection to the table corresponding to this GameTable.
    #  @param settings  The dictionary of settings for the app
    #  @param request   A request object, with information about a date range
    #                   and other information on what data to retrieve.
    def __init__(self, db, settings, request: Request):
        # Define instance vars
        self.column_names:       typing.List[str]
        self.complex_data_index: int
        self.client_time_index:  int
        self.session_id_index:   int
        self.event_index:        int
        self.level_index:        int
        self.max_level:          int
        self.min_level:          int
        self.session_ids:        typing.List[int]
        # Set instance vars
        db_cursor = db.cursor(buffered=True)
        db_settings = settings["db_config"]
        self.column_names = GameTable._getColumnNames(db_cursor, db, db_settings)
        # Take note of specific indices which will be useful when using a GameTable
        # TODO: Honestly, should just make a reverse index dictionary.
        self.complex_data_index = self.column_names.index("event_data_complex")
        self.client_time_index = self.column_names.index("client_time")
        self.session_id_index = self.column_names.index("session_id")
        self.pers_session_id_index = self.column_names.index("persistent_session_id")
        self.event_index = self.column_names.index("event")
        self.level_index = self.column_names.index("level")
        max_min_raw = utils.SQL.SELECT(cursor=db_cursor, db_name=db.database, table=db_settings["table"],
                                        columns=["MAX(level)", "MIN(level)"], filter="app_id=\"{}\"".format(request.game_id),
                                        distinct=True)
        self.max_level = max_min_raw[0][0]
        self.min_level = max_min_raw[0][1]
        self.session_ids = GameTable._getSessionIDs(db_cursor, db, db_settings, request)
        # logging.debug("session_ids: " + str(session_ids))
    
    ## Private helper function to retrieve a list of all database columns from the table.
    #  This requires executing a SQL statement, so it's slightly slower than
    #  using the schema, but is guaranteed to be correct for what's in the db.
    #  Just used to initialize the column_names member of the GameTable class.
    @staticmethod
    def _getColumnNames(db_cursor, db, db_settings):
    # TODO: Currently, this is retrieved separately from the schema. We may just want to load in one place, and check for a match or something.
        query = "SHOW COLUMNS from {}.{}".format(db.database, db_settings["table"])
        logging.info("Running query: " + query)
        start = datetime.now()
        db_cursor.execute(query)
        logging.info(f"Query execution completed, time to execute: {datetime.now()-start}")
        return [col[0] for col in db_cursor.fetchall()]
    
    ## Private helper function to get a list of all sessions within the timeframe
    #  given in the request, for the game id given in the request.
    #  Just used to initialize the session_ids member of the GameTable class.
    @staticmethod
    def _getSessionIDs(db_cursor, db, db_settings, request):
        if type(request) == Request.DateRangeRequest:
            # We grab the ids for all sessions that have 0th move in the proper date range.
            filt = "app_id=\"{}\" AND session_n=0 AND (server_time BETWEEN '{}' AND '{}')".format( \
                        request.game_id, request.start_date.isoformat(), request.end_date.isoformat())
            session_ids_raw = utils.SQL.SELECT(cursor=db_cursor, db_name=db.database, table=db_settings["table"],
                                            columns=["session_id"], filter=filt,
                                            sort_columns=["session_id"], sort_direction="ASC", distinct=True, limit=request.max_sessions)
            return [sess[0] for sess in session_ids_raw]
        elif type(request) == Request.IDListRequest:
            return request._session_ids