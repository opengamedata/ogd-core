from datetime import date

## @class Request
#  Dumb struct to hold data related to requests for data export.
#  This way, we've at least got a list of what is available in a request.
class Request:
    ## Constructor for the request class.
    #  Just stores whatever data is given. No checking done to ensure we have all
    #  necessary data, this can be checked wherever Requests are actually used.
    #  @param game_id An identifier for the game from which we want to extract data.
    #                 Should correspond to the app_id in the database.
    #  @param start_date   The starting date for our range of data to process.
    #  @param end_date     The ending date for our range of data to process.
    #  @param max_sessions Maximum number of sessions to be processed.
    #  @param min_moves    The minimum number of moves (events) per session.
    #                      Any session with fewer moves is ignored.
    # TODO: Not actually sure if I ever set up code to ignore sessions with < min_moves.
    def __init__(self, game_id: str = None, max_sessions: int = None, min_moves: int = None):
        self.game_id = game_id
        self.max_sessions = max_sessions
        self.min_moves = min_moves

class DateRangeRequest(Request):
    def __init__(self, game_id: str = None, max_sessions: int = None, min_moves: int = None,
                 start_date: date = None, end_date: date = None):
        Request.__init__(self, game_id=game_id, max_sessions=max_sessions, min_moves=min_moves)
        self.start_date = start_date
        self.end_date = end_date

    ## String representation of a request. Just gives game id, and date range.
    def __str__(self):
        fmt = "%Y%m%d"
        return f"{self.game_id}: {self.start_date.strftime(fmt)}-{self.end_date.strftime(fmt)}"

class IDListRequest(Request):
    def __init__(self, game_id: str = None, max_sessions: int = None, min_moves: int = None,
                    session_ids = []):
        Request.__init__(self, game_id=game_id, max_sessions=max_sessions, min_moves=min_moves)
        self._session_ids = session_ids