from datetime import date, datetime
from typing import Any, Dict, List, Union
Map = Dict[str, Any] # type alias: we'll call any dict using string keys a "Map"

## @class Event
#  Completely dumb struct that enforces a particular structure for the data we get from a source.
#  Basically, whenever we fetch data, the TableSchema will be used to map columns to the required elements of an Event.
#  Then the extractors etc. can just access columns in a direct manner.
class Event:
    def __init__(self, session_id:str, app_id:str,   timestamp:datetime, event_name:str, event_data:Map,
                 app_version:Union[str,None] = None, log_version:Union[str,None] = None, time_offset:Union[int,None] = None,
                 user_id:Union[str,None] = "",   user_data:Union[Map,None] = {},
                 game_state:Union[Map,None] = {}, event_sequence_index:Union[int,None] = None):
        """Constructor for an Event object.

        :param session_id: An identifier for the session during which the event occurred.
        :type  session_id: int
        :param app_id: An identifier for the app that generated the event, typically the name of a game
        :type  app_id: str
        :param timestamp: The (local) time at which the event occurred.
        :type  timestamp: datetime
        :param event_name: The "type" of the event. e.g. begin game, end game, buy item, etc.
        :type  event_name: str
        :param event_data: A "blob" of all data specific to the event type, contents vary by game and event type.
        :type  event_data: Dict[str,Any]
        :param app_version: The version of the given game that created the event.
        :type  app_version: Union[int,None], optional
        :param log_version: The version of the given game's logging code (may or may not correspond to game's versioning)
        :type  log_version: Union[int,None], optional
        :param time_offset: [description], defaults to None
        :type  time_offset: Union[int,None], optional
        :param user_id: Optional identifier for the specific user during whose session the event occurred. Defaults to None.
        :type  user_id: Union[int,None], optional
        :param user_data: [description], defaults to None
        :type  user_data: Union[Dict[str,Any],None], optional
        :param game_state: [description], defaults to None
        :type  game_state: Union[Dict[str,Any],None], optional
        :param event_sequence_index: [description], defaults to None
        :type  event_sequence_index: Union[int,None], optional
        """
        self.session_id           : str             = session_id
        self.app_id               : str             = app_id
        self.timestamp            : datetime        = timestamp
        self.event_name           : str             = event_name
        self.event_data           : Map             = event_data
        self.app_version          : str             = app_version if app_version is not None else "0"
        self.log_version          : str             = log_version if log_version is not None else "0"
        self.time_offset          : Union[int,None] = time_offset
        self.user_id              : Union[str,None] = user_id
        self.user_data            : Map             = user_data if user_data is not None else {}
        self.game_state           : Map             = game_state if game_state is not None else {}
        self.event_sequence_index : Union[int,None] = event_sequence_index

    def __str__(self):
        return f"session_id  : {self.session_id}\n"\
             + f"app_id      : {self.app_id}\n"\
             + f"timestamp   : {self.timestamp}\n"\
             + f"event_name  : {self.event_name}\n"\
             + f"event_data  : {self.event_data}\n"\
             + f"app_version : {self.app_version}\n"\
             + f"log_version : {self.log_version}\n"\
             + f"offset      : {self.time_offset}\n"\
             + f"user_id     : {self.user_id}\n"\
             + f"user_data   : {self.user_data}\n"\
             + f"game_state  : {self.game_state}\n"\
             + f"index       : {self.event_sequence_index}\n"\

    @staticmethod
    def CompareVersions(a:str, b:str, version_separator='.'):
        a_parts = [int(i) for i in a.split(version_separator)]
        b_parts = [int(i) for i in b.split(version_separator)]
        for i in range(0, min(len(a_parts), len(b_parts))):
            if a_parts[i] < b_parts[i]:
                return -1
            elif a_parts[i] > b_parts[i]:
                return 1
        if len(a_parts) < len(b_parts):
            return -1
        elif len(a_parts) > len(b_parts):
            return 1
        else:
            return 0

    @staticmethod
    def ColumnNames() -> List[str]:
        return ["session_id",  "app_id",      "timestamp", "event_name", "event_data",
                "app_version", "log_version", "offset",    "user_id",    "user_data",
                "game_state",  "index"]

    def ColumnValues(self) -> List[Union[str, datetime, Map, int, None]]:
        return [self.session_id,  self.app_id,      self.timestamp,   self.event_name,
                self.event_data,  self.app_version, self.log_version, self.time_offset,
                self.user_id,     self.user_data,   self.game_state,  self.event_sequence_index]