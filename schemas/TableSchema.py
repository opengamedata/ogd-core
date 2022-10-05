## import standard libraries
import json
from operator import concat
import os
import logging
import traceback
from datetime import datetime
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional, Union
Map = Dict[str, Any] # type alias: we'll call any dict using string keys a "Map"
## import local files
import utils
from config.config import settings as default_settings
from schemas.Event import Event, EventSource
from schemas.table_schemas.ColumnMapSchema import ColumnMapSchema
from schemas.table_schemas.ColumnSchema import ColumnSchema
from utils import Logger

## @class TableSchema
#  Dumb struct to hold useful info about the structure of database data
#  for a particular game.
#  This includes the indices of several important database columns, the names
#  of the database columns, the max and min levels in the game, and a list of
#  IDs for the game sessions in the given requested date range.
class TableSchema:

    def __init__(self, schema_name:str, schema_path:Path = Path("./") / os.path.dirname(__file__) / "TABLES/"):
        """Constructor for the TableSchema class.
        Given a database connection and a game data request,
        this retrieves a bit of information from the database to fill in the
        class variables.

        :param schema_name: The filename for the table schema JSON.
        :type schema_name: str
        :param schema_path: Path to find the given table schema file, defaults to os.path.dirname(__file__)+"/TABLES/"
        :type schema_path: str, optional
        :param is_legacy: [description], defaults to False
        :type is_legacy: bool, optional
        """
        # declare and initialize vars
        self._schema            : Optional[Dict[str, Any]]
        self._column_map        : ColumnMapSchema
        self._columns           : List[ColumnSchema]   = []
        self._table_format_name : str                  = schema_name

        if not self._table_format_name.lower().endswith(".json"):
            self._table_format_name += ".json"
        self._schema = utils.loadJSONFile(filename=self._table_format_name, path=schema_path)

        # after loading the file, take the stuff we need and store.
        if self._schema is not None:
            self._columns    = [ColumnSchema(column_details) for column_details in self._schema.get('columns', [])]
            self._column_map = ColumnMapSchema(map=self._schema.get('column_map', {}), column_names=self.ColumnNames)
        else:
            Logger.Log(f"Could not find event_data_complex schemas at {schema_path}{schema_name}", logging.ERROR)

    @staticmethod
    def FromID(game_id:str, settings:Optional[Dict[str, Any]]=None):
        if settings is not None:
            _table_name = settings["GAME_SOURCE_MAP"].get(game_id, {}).get("schema", "NO SCHEMA DEFINED")
        else:
            _table_name = default_settings["GAME_SOURCE_MAP"].get(game_id, {}).get("schema", "NO SCHEMA DEFINED")
        return TableSchema(schema_name=f"{_table_name}.json")

    @staticmethod
    def ConvertTime(time_str) -> datetime:
        ret_val : datetime

        formats = ["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"]

        for fmt in formats:
            try:
                ret_val = datetime.strptime(time_str, fmt)
            except ValueError as err:
                pass
            else:
                return ret_val
        raise ValueError(f"Could not parse timestamp {time_str}, it did not match any expected formats.")

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
        sess_id : str
        app_id  : str
        time    : datetime
        ename   : str
        edata   : Map
        app_ver : str
        log_ver : str
        offset  : Optional[int]
        uid     : Optional[str]
        udata   : Optional[Map]
        state   : Optional[Map]
        index   : Optional[int]

        # 2) Handle event_data parameter, a special case.
        #    For this case we've got to parse the json, and then fold in whatever other columns were desired.
        # 3) Assign vals to our arg vars and pass to Event ctor.
        sess_id = TableSchema._getMappedFromRow(row=row, indices=self._column_map.SessionID,   concatenator=concatenator, fallback=fallbacks.get('session_id'))
        app_id  = TableSchema._getMappedFromRow(row=row, indices=self._column_map.AppID,       concatenator=concatenator, fallback=fallbacks.get('app_id'))
        _time   = TableSchema._getMappedFromRow(row=row, indices=self._column_map.Timestamp,   concatenator=concatenator, fallback=fallbacks.get('timestamp'))
        time    = TableSchema.ConvertTime(_time)
        ename   = TableSchema._getMappedFromRow(row=row, indices=self._column_map.EventName,   concatenator=concatenator, fallback=fallbacks.get('event_name'))


        datas : Dict[str, Any] = {}
        if self._column_map.EventData is not None:
            if isinstance(self._column_map.EventData, list):
                # if we had a list of event_data columns, we need a merger, not a concatenation
                for index in self._column_map.EventData:
                    val = TableSchema._parse(input=row[index], col_schema=self._columns[index])
                    datas.update(val if isinstance(val, dict) else {self._columns[index].Name:val})
            elif isinstance(self._column_map.EventData, int):
                # if event_data is just one column, then we can just get that item
                datas = TableSchema._parse(input=row[self._column_map.EventData], col_schema=self.Columns[self._column_map.EventData])
        else:
            datas = fallbacks.get('event_data', {})
        # TODO: go bac to isostring function; need 0-padding on ms first, though
        edata   = dict(sorted(datas.items())) # Sort keys alphabetically


        esrc    = TableSchema._getMappedFromRow(row=row, indices=self._column_map.EventSource, concatenator=concatenator, fallback=fallbacks.get('event_source', EventSource.GAME))
        app_ver = TableSchema._getMappedFromRow(row=row, indices=self._column_map.AppVersion,  concatenator=concatenator, fallback=fallbacks.get('app_version'))
        log_ver = TableSchema._getMappedFromRow(row=row, indices=self._column_map.LogVersion,  concatenator=concatenator, fallback=fallbacks.get('log_version'))
        offset  = TableSchema._getMappedFromRow(row=row, indices=self._column_map.TimeOffset,  concatenator=concatenator, fallback=fallbacks.get('time_offset'))
        uid     = TableSchema._getMappedFromRow(row=row, indices=self._column_map.UserID,      concatenator=concatenator, fallback=fallbacks.get('user_id'))
        udata   = TableSchema._getMappedFromRow(row=row, indices=self._column_map.UserData,    concatenator=concatenator, fallback=fallbacks.get('user_data'))
        state   = TableSchema._getMappedFromRow(row=row, indices=self._column_map.GameState,   concatenator=concatenator, fallback=fallbacks.get('game_state'))
        index   = TableSchema._getMappedFromRow(row=row, indices=self._column_map.EventSequenceIndex, concatenator=concatenator, fallback=fallbacks.get('event_sequence_index'))


        # if self._columns[0].Name == 'event_name' and app_ver is None:
        #     if 'app_version' in params['event_data']:
        #         app_ver = str(params['event_data']['app_version']['int_value'])
        #     else:
        #         app_ver = "0"

        # if self._columns[0].Name == 'event_name' and log_ver is None:
        #     if 'log_ver' in params['event_data']:
        #         log_ver = str(params['event_data']['log_version']['int_value'])
        #     else:
        #         log_ver = "0"

        return Event(session_id=sess_id, app_id=app_id, timestamp=time,
                     event_name=ename, event_data=edata, event_source=esrc,
                     app_version=app_ver, log_version=log_ver,
                     time_offset=offset, user_id=uid, user_data=udata,
                     game_state=state, event_sequence_index=index)

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
        ret_val = "  \n\n".join([
            "## Database Columns",
            "The individual columns recorded in the database for this game.",
            "\n".join([item.AsMarkdown for item in self.Columns]),
            "\n\n## Event Object Elements",
            "The elements (member variables) of each Event object, available to programmers when writing feature extractors. The right-hand side shows which database column(s) are mapped to a given element.",
            self._column_map.AsMarkdown,
            ""])
        return ret_val

    @staticmethod
    def _getMappedFromRow(row:Tuple, indices:Union[int, List[int], None], concatenator:str, fallback:Any) -> Any:
        ret_val : Any
        if indices is not None:
            if isinstance(indices, int):
                ret_val = row[indices]
            elif isinstance(indices, list):
                ret_val = concatenator.join([str(row[index]) for index in indices])
        else:
            ret_val = fallback
        return ret_val

    @staticmethod
    def _parse(input:str, col_schema:ColumnSchema) -> Any:
        if col_schema.ValueType == 'str':
            return str(input)
        elif col_schema.ValueType == 'int':
            return int(input)
        elif col_schema.ValueType == 'float':
            return float(input)
        elif col_schema.ValueType == 'datetime':
            return str(input)
        elif col_schema.ValueType == 'json':
            if input != 'None': # watch out for nasty corner case.
                try:
                    return json.loads(str(input))
                except JSONDecodeError as err:
                    Logger.Log(f"Could not parse input '{input}' of type {type(input)} from column {col_schema.Name}, got the following error:\n{str(err)}", logging.WARN)
                    return {}
            else:
                return None
        elif col_schema.ValueType.startswith('enum'):
            # if the column is supposed to be an enum, for now we just stick with the string.
            return str(input)
    

    # # parse out complex data from json
    # col = event[game_table.complex_data_index]
    # try:
    #     # complex_data_parsed = json.loads(col.replace("'", "\"")) if (col is not None) else {"event_custom":row[game_table.event_index]}
    #     complex_data_parsed = json.loads(col) if (col is not None) else {"event_custom":event[game_table.event_index]}
    # except Exception as err:
    #     msg = f"When trying to parse {col}, get error\n{type(err)} {str(err)}"
    #     Logger.Log(msg, logging.ERROR)
    #     raise err

    # # make sure we get *something* in the event_custom name
    # # TODO: Make a better solution for games without event_custom fields in the logs themselves
    # if self._game_id == 'LAKELAND' or self._game_id == 'JOWILDER':
    #     if type(complex_data_parsed) is not type({}):
    #         complex_data_parsed = {"item": complex_data_parsed}
    #     complex_data_parsed["event_custom"] = event[game_table.event_custom_index]
    # elif "event_custom" not in complex_data_parsed.keys():
    #     complex_data_parsed["event_custom"] = event[game_table.event_index]
    # # replace the json with parsed version.
    # m_row = list(event)
    # m_row[game_table.complex_data_index] = complex_data_parsed
    # event = tuple(m_row)
