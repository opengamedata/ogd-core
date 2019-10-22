## import standard libraries
import logging
import typing
from datetime import datetime
## import local files
import Request
import utils
from schemas.Schema import Schema

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
    def __init__(self, db, settings, request: Request,
                 err_logger: logging.Logger, std_logger: logging.Logger):
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
        self._err_logger:        logging.Logger   = err_logger
        self._std_logger:        logging.Logger   = std_logger
        # Set instance vars
        db_cursor = db.cursor()
        db_settings = settings["db_config"]
        self.column_names = GameTable._getColumnNames(db_cursor, db, db_settings)
        # Take note of specific indices which will be useful when using a GameTable
        # TODO: Honestly, should just make a reverse index dictionary.
        self.complex_data_index = self.column_names.index("event_data_complex")
        self.client_time_index = self.column_names.index("client_time")
        self.server_time_index = self.column_names.index("server_time")
        self.session_id_index = self.column_names.index("session_id")
        self.pers_session_id_index = self.column_names.index("persistent_session_id")
        self.event_index = self.column_names.index("event")
        self.event_custom_index = self.column_names.index("event_custom")
        self.level_index = self.column_names.index("level")
        if request.game_id == "WAVES":
            self.max_level = 34
            self.min_level = 0
        else:
            max_min_raw = utils.SQL.SELECT(cursor=db_cursor, db_name=db_settings["DB_NAME_DATA"], table=db_settings["table"],
                                            columns=["MAX(level)", "MIN(level)"], filter=f"`app_id`='{request.game_id}'",
                                            distinct=True)
            self.max_level = max_min_raw[0][0]
            self.min_level = max_min_raw[0][1]
        if request.game_id == 'LAKELAND':
            self.playtimes = utils.SQL.SELECT(cursor=db_cursor, db_name=db_settings["DB_NAME_DATA"], table=db_settings["table"],
                                            columns=["MAX(client_time)", "MIN(client_time)"], grouping='session_id', filter="`app_id`=\"{}\"".format(request.game_id),
                                            distinct=True)
            play_durations = [p[0]-p[1] for p in self.playtimes]
            max_play_duration = max(play_durations)
            self.min_level = 0
            self.max_level = max_play_duration.seconds // Schema('LAKELAND').schema()['config']['WINDOW_SIZE_SECONDS']
        self.session_ids = request.retrieveSessionIDs(db_cursor=db_cursor, db_settings=db_settings)
        # logging.debug("session_ids: " + str(session_ids))
    
    ## Private helper function to retrieve a list of all database columns from the table.
    #  This requires executing a SQL statement, so it's slightly slower than
    #  using the schema, but is guaranteed to be correct for what's in the db.
    #  Just used to initialize the column_names member of the GameTable class.
    @staticmethod
    def _getColumnNames(db_cursor, db, db_settings):
    # TODO: Currently, this is retrieved separately from the schema. We may just want to load in one place, and check for a match or something.
        query = "SHOW COLUMNS from {}.{}".format(db_settings["DB_NAME_DATA"], db_settings["table"])
        return utils.SQL.Query(cursor=db_cursor, query=query)