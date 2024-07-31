## import standard libraries
import json
import logging
import re
from dateutil import parser
from datetime import datetime, time, timedelta, timezone
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Any, Dict, Final, List, Tuple, Optional, Union
## import local files
from ogd.core import schemas
from ogd.core.models.Event import Event, EventSource
from ogd.core.schemas.tables.ColumnMapSchema import ColumnMapSchema
from ogd.core.schemas.tables.ColumnSchema import ColumnSchema
from ogd.core.utils import utils
from ogd.core.utils.Logger import Logger
from ogd.core.utils.typing import Map

## @class TableSchema
#  Dumb struct to hold useful info about the structure of database data
#  for a particular game.
#  This includes the indices of several important database columns, the names
#  of the database columns, the max and min levels in the game, and a list of
#  IDs for the game sessions in the given requested date range.
class TableSchema:

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, schema_name:str, schema_path:Path = Path(schemas.__file__).parent / "table_schemas/"):
        """Constructor for the TableSchema class.
        Given a database connection and a game data request,
        this retrieves a bit of information from the database to fill in the
        class variables.

        :param schema_name: The filename for the table schema JSON.
        :type schema_name: str
        :param schema_path: Path to find the given table schema file, defaults to "./schemas/table_schemas/"
        :type schema_path: str, optional
        :param is_legacy: [description], defaults to False
        :type is_legacy: bool, optional
        """
        # declare and initialize vars
        self._schema            : Optional[Dict[str, Any]]
        self._column_map        : ColumnMapSchema
        self._columns           : List[ColumnSchema] = []
        self._table_format_name : str                    = schema_name

        if not self._table_format_name.lower().endswith(".json"):
            self._table_format_name += ".json"
        self._schema = utils.loadJSONFile(filename=self._table_format_name, path=schema_path)

        # after loading the file, take the stuff we need and store.
        if self._schema is not None:
            self._columns    = [ColumnSchema(column_details) for column_details in self._schema.get('columns', [])]
            self._column_map = ColumnMapSchema(map=self._schema.get('column_map', {}), column_names=self.ColumnNames)
        else:
            Logger.Log(f"Could not find event_data_complex schemas at {schema_path}{schema_name}", logging.ERROR)

    @property
    def ColumnNames(self) -> List[str]:
        """Function to get the names of all columns in the schema.

        :return: Names of each column in the schema.
        :rtype: List[str]
        """
        return [col.Name for col in self._columns]

    @property
    def Columns(self) -> List[ColumnSchema]:
        return self._columns

    @property
    def AsMarkdown(self) -> str:
        ret_val = "\n\n".join([
            "## Database Columns",
            "The individual columns recorded in the database for this game.",
            "\n".join([item.AsMarkdown for item in self.Columns]),
            "## Event Object Elements",
            "The elements (member variables) of each Event object, available to programmers when writing feature extractors. The right-hand side shows which database column(s) are mapped to a given element.",
            self._column_map.AsMarkdown,
            ""])
        return ret_val

    @property
    def SessionIDColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self._column_map.SessionID, int):
            ret_val = self.ColumnNames[self._column_map.SessionID]
        elif isinstance(self._column_map.SessionID, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self._column_map.SessionID])
        return ret_val

    @property
    def AppIDColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self._column_map.AppID, int):
            ret_val = self.ColumnNames[self._column_map.AppID]
        elif isinstance(self._column_map.AppID, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self._column_map.AppID])
        return ret_val

    @property
    def TimestampColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self._column_map.Timestamp, int):
            ret_val = self.ColumnNames[self._column_map.Timestamp]
        elif isinstance(self._column_map.Timestamp, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self._column_map.Timestamp])
        return ret_val

    @property
    def EventNameColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self._column_map.EventName, int):
            ret_val = self.ColumnNames[self._column_map.EventName]
        elif isinstance(self._column_map.EventName, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self._column_map.EventName])
        return ret_val

    @property
    def EventDataColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self._column_map.EventData, int):
            ret_val = self.ColumnNames[self._column_map.EventData]
        elif isinstance(self._column_map.EventData, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self._column_map.EventData])
        return ret_val

    @property
    def EventSourceColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self._column_map.EventSource, int):
            ret_val = self.ColumnNames[self._column_map.EventSource]
        elif isinstance(self._column_map.EventSource, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self._column_map.EventSource])
        return ret_val

    @property
    def AppVersionColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self._column_map.AppVersion, int):
            ret_val = self.ColumnNames[self._column_map.AppVersion]
        elif isinstance(self._column_map.AppVersion, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self._column_map.AppVersion])
        return ret_val

    @property
    def AppBranchColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self._column_map.AppBranch, int):
            ret_val = self.ColumnNames[self._column_map.AppBranch]
        elif isinstance(self._column_map.AppBranch, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self._column_map.AppBranch])
        return ret_val

    @property
    def LogVersionColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self._column_map.LogVersion, int):
            ret_val = self.ColumnNames[self._column_map.LogVersion]
        elif isinstance(self._column_map.LogVersion, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self._column_map.LogVersion])
        return ret_val

    @property
    def TimeOffsetColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self._column_map.TimeOffset, int):
            ret_val = self.ColumnNames[self._column_map.TimeOffset]
        elif isinstance(self._column_map.TimeOffset, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self._column_map.TimeOffset])
        return ret_val

    @property
    def UserIDColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self._column_map.UserID, int):
            ret_val = self.ColumnNames[self._column_map.UserID]
        elif isinstance(self._column_map.UserID, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self._column_map.UserID])
        return ret_val

    @property
    def UserDataColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self._column_map.UserData, int):
            ret_val = self.ColumnNames[self._column_map.UserData]
        elif isinstance(self._column_map.UserData, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self._column_map.UserData])
        return ret_val

    @property
    def GameStateColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self._column_map.GameState, int):
            ret_val = self.ColumnNames[self._column_map.GameState]
        elif isinstance(self._column_map.GameState, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self._column_map.GameState])
        return ret_val

    @property
    def EventSequenceIndexColumn(self) -> Optional[str]:
        ret_val = None
        if isinstance(self._column_map.EventSequenceIndex, int):
            ret_val = self.ColumnNames[self._column_map.EventSequenceIndex]
        elif isinstance(self._column_map.EventSequenceIndex, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in self._column_map.EventSequenceIndex])
        return ret_val

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    _conversion_warnings = []
    def RowToEvent(self, row:Tuple, concatenator:str = '.', fallbacks:utils.map={}):
        """Function to convert a row to an Event, based on the loaded schema.
        In general, columns specified in the schema's column_map are mapped to corresponding elements of the Event.
        If the column_map gave a list, rather than a single column name, the values from each column are concatenated in order with '.' character separators.
        Finally, the concatenated values (or single value) are parsed according to the type required by Event.
        One exception: For event_data, we expect to create a Dict object, so each column in the list will have its value parsed according to the type in 'columns',
            and placed into a dict mapping the original column name to the parsed value (unless the parsed value is a dict, then it is merged into the top-level dict).

        :param row: The raw row data for an event. Generally assumed to be a tuple, though in principle a list would be fine too.
        :type  row: Tuple[str]
        :param concatenator: A string to use as a separator when concatenating multiple columns into a single Event element.
        :type  concatenator: str
        :return: [description]
        :rtype: [type]
        """
        # define vars to be passed as params
        MAX_WARNINGS : Final[int] = 10
        sess_id : str
        app_id  : str
        time    : datetime
        ename   : str
        edata   : Map
        app_ver : str
        app_br  : str
        log_ver : str
        offset  : Optional[timezone]
        uid     : Optional[str]
        udata   : Optional[Map]
        state   : Optional[Map]
        index   : Optional[int]

        # 2) Handle event_data parameter, a special case.
        #    For this case we've got to parse the json, and then fold in whatever other columns were desired.
        # 3) Assign vals to our arg vars and pass to Event ctor.
        sess_id = self._getValueFromRow(row=row, indices=self._column_map.SessionID,   concatenator=concatenator, fallback=fallbacks.get('session_id'))
        if not isinstance(sess_id, str):
            if "sess_id" not in TableSchema._conversion_warnings:
                Logger.Log(f"{self._table_format_name} table schema set session_id as {type(sess_id)}, but session_id should be a string", logging.WARN)
                TableSchema._conversion_warnings.append("sess_id")
            sess_id = str(sess_id)

        app_id  = self._getValueFromRow(row=row, indices=self._column_map.AppID,       concatenator=concatenator, fallback=fallbacks.get('app_id'))
        if not isinstance(app_id, str):
            if "app_id" not in TableSchema._conversion_warnings:
                Logger.Log(f"{self._table_format_name} table schema set app_id as {type(app_id)}, but app_id should be a string", logging.WARN)
                TableSchema._conversion_warnings.append("app_id")
            app_id = str(app_id)

        time   = self._getValueFromRow(row=row, indices=self._column_map.Timestamp,   concatenator=concatenator, fallback=fallbacks.get('timestamp'))
        if not isinstance(time, datetime):
            if "timestamp" not in TableSchema._conversion_warnings:
                Logger.Log(f"{self._table_format_name} table schema parsed timestamp as {type(time)}, but timestamp should be a datetime", logging.WARN)
                TableSchema._conversion_warnings.append("timestamp")
            time = TableSchema._convertDateTime(time)

        ename   = self._getValueFromRow(row=row, indices=self._column_map.EventName,   concatenator=concatenator, fallback=fallbacks.get('event_name'))
        if not isinstance(ename, str):
            if "ename" not in TableSchema._conversion_warnings:
                Logger.Log(f"{self._table_format_name} table schema set event_name as {type(ename)}, but event_name should be a string", logging.WARN)
                TableSchema._conversion_warnings.append("ename")
            ename = str(ename)

        datas : Dict[str, Any] = self._getValueFromRow(row=row, indices=self._column_map.EventData,   concatenator=concatenator, fallback=fallbacks.get('event_data'))

        # TODO: go bac to isostring function; need 0-padding on ms first, though
        edata   = dict(sorted(datas.items())) # Sort keys alphabetically

        esrc    = self._getValueFromRow(row=row, indices=self._column_map.EventSource, concatenator=concatenator, fallback=fallbacks.get('event_source', EventSource.GAME))
        if not isinstance(esrc, EventSource):
            if "esrc" not in TableSchema._conversion_warnings:
                Logger.Log(f"{self._table_format_name} table schema set event_source as {type(esrc)}, but event_source should be an EventSource", logging.WARN)
                TableSchema._conversion_warnings.append("esrc")
            esrc = EventSource.GENERATED if esrc == "GENERATED" else EventSource.GAME

        app_ver = self._getValueFromRow(row=row, indices=self._column_map.AppVersion,  concatenator=concatenator, fallback=fallbacks.get('app_version', "0"))
        if not isinstance(app_ver, str):
            if "app_ver" not in TableSchema._conversion_warnings:
                Logger.Log(f"{self._table_format_name} table schema set app_version as {type(app_ver)}, but app_version should be a string", logging.WARN)
                TableSchema._conversion_warnings.append("app_ver")
            app_ver = str(app_ver)

        app_br = self._getValueFromRow(row=row, indices=self._column_map.AppBranch,  concatenator=concatenator, fallback=fallbacks.get('app_branch'))
        if not isinstance(app_br, str):
            if "app_br" not in TableSchema._conversion_warnings:
                Logger.Log(f"{self._table_format_name} table schema set app_branch as {type(app_br)}, but app_branch should be a string", logging.WARN)
                TableSchema._conversion_warnings.append("app_br")
            app_br = str(app_br)

        log_ver = self._getValueFromRow(row=row, indices=self._column_map.LogVersion,  concatenator=concatenator, fallback=fallbacks.get('log_version', "0"))
        if not isinstance(log_ver, str):
            if "log_ver" not in TableSchema._conversion_warnings:
                Logger.Log(f"{self._table_format_name} table schema set log_version as {type(log_ver)}, but log_version should be a string", logging.WARN)
                TableSchema._conversion_warnings.append("log_ver")
            log_ver = str(log_ver)

        offset = self._getValueFromRow(row=row, indices=self._column_map.TimeOffset,  concatenator=concatenator, fallback=fallbacks.get('time_offset'))
        if isinstance(offset, timedelta):
            if "offset" not in TableSchema._conversion_warnings:
                Logger.Log(f"{self._table_format_name} table schema set offset as {type(offset)}, but offset should be a timezone", logging.WARN)
                TableSchema._conversion_warnings.append("offset")
            offset = timezone(offset)

        uid     = self._getValueFromRow(row=row, indices=self._column_map.UserID,      concatenator=concatenator, fallback=fallbacks.get('user_id'))
        if uid is not None and not isinstance(uid, str):
            if "uid" not in TableSchema._conversion_warnings:
                Logger.Log(f"{self._table_format_name} table schema set user_id as {type(uid)}, but user_id should be a string", logging.WARN)
                TableSchema._conversion_warnings.append("uid")
            uid = str(uid)

        udata   = self._getValueFromRow(row=row, indices=self._column_map.UserData,    concatenator=concatenator, fallback=fallbacks.get('user_data'))

        state   = self._getValueFromRow(row=row, indices=self._column_map.GameState,   concatenator=concatenator, fallback=fallbacks.get('game_state'))

        index   = self._getValueFromRow(row=row, indices=self._column_map.EventSequenceIndex, concatenator=concatenator, fallback=fallbacks.get('event_sequence_index'))
        if index is not None and not isinstance(index, int):
            if "index" not in TableSchema._conversion_warnings:
                Logger.Log(f"{self._table_format_name} table schema set event_sequence_index as {type(index)}, but event_sequence_index should be an int", logging.WARN)
                TableSchema._conversion_warnings.append("index")
            index = int(index)

        return Event(session_id=sess_id, app_id=app_id, timestamp=time,
                     event_name=ename, event_data=edata, event_source=esrc,
                     app_version=app_ver, app_branch=app_br, log_version=log_ver,
                     time_offset=offset, user_id=uid, user_data=udata,
                     game_state=state, event_sequence_index=index)

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parse(input:Any, col_schema:ColumnSchema) -> Any:
        """Applies whatever parsing is appropriate based on what type the schema said a column contained.

        :param input: _description_
        :type input: str
        :param col_schema: _description_
        :type col_schema: ColumnSchema
        :return: _description_
        :rtype: Any
        """
        if input is None:
            return None
        if input == "None" or input == "null" or input == "nan":
            return None
        elif col_schema.ValueType == 'str':
            return str(input)
        elif col_schema.ValueType == 'int':
            return int(input)
        elif col_schema.ValueType == 'float':
            return float(input)
        elif col_schema.ValueType == 'datetime':
            return input if isinstance(input, datetime) else TableSchema._convertDateTime(str(input))
        elif col_schema.ValueType == 'timedelta':
            return input if isinstance(input, timedelta) else TableSchema._convertTimedelta(str(input))
        elif col_schema.ValueType == 'timezone':
            return input if isinstance(input, timezone) else TableSchema._convertTimezone(str(input))
        elif col_schema.ValueType == 'json':
            try:
                if isinstance(input, dict):
                    # if input was a dict already, then just give it back. Else, try to load it from string.
                    return input
                elif isinstance(input, str):
                    if input != 'None' and input != '': # watch out for nasty corner cases.
                        return json.loads(input)
                    else:
                        return None
                else:
                    return json.loads(str(input))
            except JSONDecodeError as err:
                Logger.Log(f"Could not parse input '{input}' of type {type(input)} from column {col_schema.Name}, got the following error:\n{str(err)}", logging.WARN)
                return {}
        elif col_schema.ValueType.startswith('enum'):
            # if the column is supposed to be an enum, for now we just stick with the string.
            return str(input)

    @staticmethod
    def _convertDateTime(time_str:str) -> datetime:
        ret_val : datetime

        if time_str == "None" or time_str == "none" or time_str == "null" or time_str == "nan":
            raise ValueError(f"Got a non-timestamp value of {time_str} when converting a datetime column of an Event!")

        formats = ["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S.%f"]

        # for fmt in formats:
        try:
            ret_val = parser.isoparse(time_str)
            # ret_val = datetime.strptime(time_str, fmt)
        except ValueError as err:
            Logger.Log(f"Could not parse time string '{time_str}', got error {err}")
            raise err
        else:
            return ret_val
        # raise ValueError(f"Could not parse timestamp {time_str}, it did not match any expected formats.")

    @staticmethod
    def _convertTimedelta(time_str:str) -> Optional[timedelta]:
        ret_val : Optional[timedelta]

        if time_str == "None" or time_str == "none" or time_str == "null" or time_str == "nan":
            return None
        elif re.fullmatch(pattern=r"\d+:\d+:\d+(\.\d+)?", string=time_str):
            try:
                pieces = time_str.split(':')
                seconds_pieces = pieces[2].split('.')
                ret_val = timedelta(hours=int(pieces[0]),
                                    minutes=int(pieces[1]),
                                    seconds=int(seconds_pieces[0]),
                                    milliseconds=int(seconds_pieces[1]) if len(seconds_pieces) > 1 else 0)
            except ValueError as err:
                pass
            except IndexError as err:
                pass
            else:
                return ret_val
        elif re.fullmatch(pattern=r"-?\d+", string=time_str):
            try:
                ret_val = timedelta(seconds=int(time_str))
            except ValueError as err:
                pass
            else:
                return ret_val
        raise ValueError(f"Could not parse timedelta {time_str} of type {type(time_str)}, it did not match any expected formats.")

    @staticmethod
    def _convertTimezone(time_str:str) -> Optional[timezone]:
        ret_val : Optional[timezone]

        if time_str == "None" or time_str == "none" or time_str == "null" or time_str == "nan":
            return None
        elif re.fullmatch(pattern=r"UTC[+-]\d+:\d+", string=time_str):
            try:
                pieces = time_str.removeprefix("UTC").split(":")
                ret_val = timezone(timedelta(hours=int(pieces[0]), minutes=int(pieces[1])))
            except ValueError as err:
                pass
            else:
                return ret_val
        raise ValueError(f"Could not parse timezone {time_str} of type {type(time_str)}, it did not match any expected formats.")

    # *** PRIVATE METHODS ***

    def _getValueFromRow(self, row:Tuple, indices:Union[int, List[int], Dict[str, int], None], concatenator:str, fallback:Any) -> Any:
        ret_val : Any
        if indices is not None:
            if isinstance(indices, int):
                # if there's a single index, use parse to get the value it is stated to be
                # print(f"About to parse value {row[indices]} as type {self.Columns[indices]},\nFull list from row is {row},\nFull list of columns is {self.Columns},\nwith names {self.ColumnNames}")
                ret_val = TableSchema._parse(input=row[indices], col_schema=self.Columns[indices])
            elif isinstance(indices, list):
                ret_val = concatenator.join([str(row[index]) for index in indices])
            elif isinstance(indices, dict):
                ret_val = {}
                for key,column_index in indices.items():
                    if column_index > len(row):
                        Logger.Log(f"Got column index of {column_index} for column {key}, but row only has {len(row)} columns!", logging.ERROR)
                    _val = TableSchema._parse(input=row[column_index], col_schema=self._columns[column_index])
                    ret_val.update(_val if isinstance(_val, dict) else {key:_val})
        else:
            ret_val = fallback
        return ret_val
