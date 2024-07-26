import logging
from datetime import date, datetime, timedelta, timezone
from enum import IntEnum
from typing import Dict, List, Optional, Union

from ogd.core.utils import utils
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
                 app_version:Optional[str] = None,     app_branch:Optional[str] = None,
                 log_version:Optional[str] = None,     time_offset:Optional[timezone] = None,
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
        self.app_branch           : str           = app_branch  if app_branch  is not None else "main"
        self.log_version          : str           = log_version if log_version is not None else "0"
        self.time_offset          : Optional[timezone] = time_offset
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
             + f"app_branch   : {self.app_branch}\n"\
             + f"log_version  : {self.log_version}\n"\
             + f"offset       : {self.TimeOffsetString}\n"\
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
    def FromJSON(json_data:Dict):
        return Event(
            session_id  =json_data.get("session_id", "SESSION ID NOT FOUND"),
            app_id      =json_data.get("app_id", "APP ID NOT FOUND"),
            timestamp   =json_data.get("client_time", "CLIENT TIME NOT FOUND"),
            event_name  =json_data.get("event_name", "EVENT NAME NOT FOUND"),
            event_data  =json_data.get("event_data", "EVENT DATA NOT FOUND"),
            event_source=EventSource.GAME,
            app_version =json_data.get("app_version", None),
            app_branch  =json_data.get("app_branch", None),
            log_version =json_data.get("log_version", None),
            time_offset =None,
            user_id     =json_data.get("user_id", None),
            user_data   =json_data.get("user_data", None),
            game_state  =json_data.get("game_state", None),
            event_sequence_index=json_data.get("event_sequence_index", json_data).get("session_n", None)
        )

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
        return ["session_id",  "app_id",       "timestamp",   "event_name",
                "event_data",  "event_source", "app_version", "app_branch",
                "log_version", "offset",        "user_id",    "user_data",
                "game_state",  "index"]

    def ColumnValues(self) -> List[Union[str, datetime, timezone, utils.map, int, None]]:
        """A list of all values for the row, in order they appear in the `ColumnNames` function.

        .. todo:: Technically, this should be string representations of each, but we're technically not enforcing that yet.

        :return: The list of values.
        :rtype: List[Union[str, datetime, timezone, utils.map, int, None]]
        """
        return [self.session_id,  self.app_id,             self.timestamp,   self.event_name,
                self.event_data,  self.event_source.name,  self.app_version, self.app_branch,
                self.log_version, self.TimeOffsetString,   self.user_id,     self.user_data,
                self.game_state,  self.event_sequence_index]

    @property
    def SessionID(self) -> str:
        """The Session ID of the session that generated the Event

        Generally, this will be a numeric string.
        Every session ID is unique (with high probability) from all other sessions.

        :return: The Session ID of the session that generated the Event
        :rtype: str
        """
        return self.session_id

    @property
    def AppID(self) -> str:
        """The Application ID of the game that generated the Event

        Generally, this will be the game's name, or some abbreviation of the name.

        :return: The Application ID of the game that generated the Event
        :rtype: str
        """
        return self.app_id

    @property
    def Timestamp(self) -> datetime:
        """A UTC timestamp of the moment at which the game client sent the Event

        The timestamp is based on the GMT timezone, in keeping with UTC standards.
        Some legacy games may provide the time based on a local time zone, rather than GMT.

        :return: A UTC timestamp of the moment at which the game client sent the event
        :rtype: datetime
        """
        return self.timestamp

    @property
    def TimeOffset(self) -> Optional[timezone]:
        """A timedelta for the offset from GMT to the local time zone of the game client that sent the Event

        Some legacy games do not include an offset, and instead log the Timestamp based on the local time zone.

        :return: A timedelta for the offset from GMT to the local time zone of the game client that sent the Event
        :rtype: Optional[timedelta]
        """
        return self.time_offset

    @property
    def TimeOffsetString(self) -> Optional[str]:
        """A string representation of the offset from GMT to the local time zone of the game client that sent the Event

        Some legacy games do not include an offset, and instead log the Timestamp based on the local time zone.

        :return: A timedelta for the offset from GMT to the local time zone of the game client that sent the Event
        :rtype: Optional[timedelta]
        """
        return self.time_offset.tzname(None) if self.time_offset is not None else None

    @property
    def EventName(self) -> str:
        """The name of the specific type of event that occurred

        For some legacy games, the names in this column have a format of CUSTOM.1, CUSTOM.2, etc.
        For these games, the actual human-readable event names for these events are stored in the EventData column.
        Please see individual game logging documentation for details.

        :return: The name of the specific type of event that occurred
        :rtype: str
        """
        return self.event_name

    @property
    def EventData(self) -> utils.map:
        """A dictionary containing data specific to Events of this type.

        For details, see the documentation in the given game's README.md, included with all datasets.
        Alternately, review the {GAME_NAME}.json file for the given game.

        :return: A dictionary containing data specific to Events of this type
        :rtype: Dict[str, Any]
        """
        return self.event_data

    @property
    def EventSource(self) -> EventSource:
        """An enum indicating whether the event was generated directly by the game, or calculated by a post-hoc detector.

        :return: An enum indicating whether the event was generated directly by the game, or calculated by a post-hoc detector
        :rtype: EventSource
        """
        return self.event_source

    @property
    def AppVersion(self) -> str:
        """The semantic versioning string for the game that generated this Event.

        Some legacy games may use a single integer or a string similar to AppID in this column.

        :return: The semantic versioning string for the game that generated this Event
        :rtype: str
        """
        return self.app_version

    @property
    def AppBranch(self) -> str:
        """The name of the branch of a game version that generated this Event.

        The branch name is typically used for cases where multiple experimental versions of a game are deployed in parallel;
        most events will simply have a branch of "main" or "master."

        :return: The name of the branch of a game version that generated this Event
        :rtype: str
        """
        return self.app_branch

    @property
    def LogVersion(self) -> str:
        """The version of the logging schema implemented in the game that generated the Event

        For most games, this is a single integer; however, semantic versioning is valid for this column as well.

        :return: The version of the logging schema implemented in the game that generated the Event
        :rtype: str
        """
        return self.log_version

    @property
    def UserID(self) -> Optional[str]:
        """A persistent ID for a given user, identifying the individual across multiple gameplay sessions

        This identifier is only included by games with a mechanism for individuals to resume play in a new session.

        :return: A persistent ID for a given user, identifying the individual across multiple gameplay sessions
        :rtype: Optional[str]
        """
        return self.user_id

    @property
    def UserData(self) -> utils.map:
        """A dictionary containing any user-specific data tracked across gameplay sessions or individual games.

        :return: A dictionary containing any user-specific data tracked across gameplay sessions or individual games
        :rtype: Dict[str, Any]
        """
        return self.user_data

    @property
    def GameState(self) -> utils.map:
        """A dictionary containing any game-specific data that is defined across all event types in the given game.

        This column typically includes data that offers context to a given Event's data in the EventData column.
        For example, this column would typically include a level number or quest name for whatever level/quest the user was playing when the Event occurred.

        :return: A dictionary containing any game-specific data that is defined across all event types in the given game
        :rtype: Dict[str, Any]
        """
        return self.game_state

    @property
    def EventSequenceIndex(self) -> Optional[int]:
        """A strictly-increasing counter indicating the order of events in a session.

        The first event in a session has EventSequenceIndex == 0, the next has index == 1, etc.

        :return: A strictly-increasing counter indicating the order of events in a session
        :rtype: int
        """
        return self.event_sequence_index
