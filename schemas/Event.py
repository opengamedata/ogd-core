import logging
from datetime import date, datetime, timedelta
from enum import IntEnum
from typing import List, Optional, Union

import utils
class EventSource(IntEnum):
    GAME = 1
    GENERATED = 2

## @class Event
#  Completely dumb struct that enforces a particular structure for the data we get from a source.
#  Basically, whenever we fetch data, the TableSchema will be used to map columns to the required elements of an Event.
#  Then the extractors etc. can just access columns in a direct manner.
class Event:
    def __init__(self, session_id:str, app_id:str,     timestamp:datetime,
                 event_name:str, event_data:utils.map, event_source:EventSource,
                 app_version:Optional[str] = None,     log_version:Optional[str] = None,
                 time_offset:Optional[timedelta] = None,
                 user_id:Optional[str] = "",           user_data:Optional[utils.map] = {},
                 game_state:Optional[utils.map] = {},  event_sequence_index:Optional[int] = None):
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
        :type  app_version: Optional[int], optional
        :param log_version: The version of the given game's logging code (may or may not correspond to game's versioning)
        :type  log_version: Optional[int], optional
        :param time_offset: [description], defaults to None
        :type  time_offset: Optional[int], optional
        :param user_id: Optional identifier for the specific user during whose session the event occurred. Defaults to None.
        :type  user_id: Optional[int], optional
        :param user_data: [description], defaults to None
        :type  user_data: Optional[Dict[str,Any]], optional
        :param game_state: [description], defaults to None
        :type  game_state: Optional[Dict[str,Any]], optional
        :param event_sequence_index: [description], defaults to None
        :type  event_sequence_index: Optional[int], optional
        """
        # TODO: event source, e.g. from game or from detector
        self.session_id           : str           = session_id
        self.app_id               : str           = app_id
        self.timestamp            : datetime      = timestamp
        self.event_name           : str           = event_name
        self.event_data           : utils.map     = event_data
        self.event_source         : EventSource   = event_source
        self.app_version          : str           = app_version if app_version is not None else "0"
        self.log_version          : str           = log_version if log_version is not None else "0"
        self.time_offset          : Optional[timedelta] = time_offset
        self.user_id              : Optional[str] = user_id
        self.user_data            : utils.map     = user_data if user_data is not None else {}
        self.game_state           : utils.map     = game_state if game_state is not None else {}
        self.event_sequence_index : Optional[int] = event_sequence_index

    def __str__(self):
        return f"session_id   : {self.session_id}\n"\
             + f"app_id       : {self.app_id}\n"\
             + f"timestamp    : {self.timestamp}\n"\
             + f"event_name   : {self.event_name}\n"\
             + f"event_data   : {self.event_data}\n"\
             + f"event_source : {self.event_source.name}\n"\
             + f"app_version  : {self.app_version}\n"\
             + f"log_version  : {self.log_version}\n"\
             + f"offset       : {self.time_offset}\n"\
             + f"user_id      : {self.user_id}\n"\
             + f"user_data    : {self.user_data}\n"\
             + f"game_state   : {self.game_state}\n"\
             + f"index        : {self.event_sequence_index}\n"\

    def FallbackDefaults(self, app_id:Optional[str]=None, index:Optional[int]=None):
        if self.app_id == None and app_id != None:
            self.app_id = app_id
        if self.event_sequence_index == None:
            self.event_sequence_index = index

    @staticmethod
    def CompareVersions(a:str, b:str, version_separator='.') -> int:
        a_parts : Optional[List[int]]
        b_parts : Optional[List[int]]
        try:
            a_parts = [int(i) for i in a.split(version_separator)]
        except ValueError:
            a_parts = None
        try:
            b_parts = [int(i) for i in b.split(version_separator)]
        except ValueError:
            b_parts = None

        if a_parts is not None and b_parts is not None:
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
        else:
            # try to do some sort of sane handling in case we got null values for a version
            if a_parts is None and b_parts is None:
                utils.Logger.Log(f"Got invalid values of {a} & {b} for versions a & b!", logging.ERROR)
                return 0
            elif a_parts is None:
                utils.Logger.Log(f"Got invalid value of {a} for version a!", logging.ERROR)
                return 1
            elif b_parts is None:
                utils.Logger.Log(f"Got invalid value of {b} for version b!", logging.ERROR)
                return -1
        return 0 # should never reach here; just putting this here to satisfy linter

    @staticmethod
    def ColumnNames() -> List[str]:
        return ["session_id", "app_id",       "timestamp",   "event_name",
                "event_data", "event_source", "app_version", "log_version",
                "offset",     "user_id",      "user_data",   "game_state",
                "index"]

    def ColumnValues(self) -> List[Union[str, datetime, timedelta, utils.map, int, None]]:
        return [self.session_id,  self.app_id,             self.timestamp,   self.event_name,
                self.event_data,  self.event_source.name,  self.app_version, self.log_version,
                self.time_offset, self.user_id,            self.user_data,   self.game_state,
                self.event_sequence_index]

    @property
    def SessionID(self) -> str:
        return self.session_id

    @property
    def AppID(self) -> str:
        return self.app_id

    @property
    def Timestamp(self) -> datetime:
        return self.timestamp

    @property
    def EventName(self) -> str:
        return self.event_name

    @property
    def EventData(self) -> utils.map:
        return self.event_data

    @property
    def EventSource(self) -> EventSource:
        return self.event_source

    @property
    def AppVersion(self) -> str:
        return self.app_version

    @property
    def LogVersion(self) -> str:
        return self.log_version

    @property
    def TimeOffset(self) -> Optional[timedelta]:
        return self.time_offset

    @property
    def UserID(self) -> Optional[str]:
        return self.user_id

    @property
    def UserData(self) -> utils.map:
        return self.user_data

    @property
    def GameState(self) -> utils.map:
        return self.game_state

    @property
    def EventSequenceIndex(self) -> Optional[int]:
        return self.event_sequence_index
