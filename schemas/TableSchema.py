## import standard libraries
from datetime import datetime
import json
from json.decoder import JSONDecodeError
import os
import logging
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union
Map = Dict[str, Any] # type alias: we'll call any dict using string keys a "Map"
## import local files
import utils
from schemas.Event import Event

## @class TableSchema
#  Dumb struct to hold useful info about the structure of database data
#  for a particular game.
#  This includes the indices of several important database columns, the names
#  of the database columns, the max and min levels in the game, and a list of
#  IDs for the game sessions in the given requested date range.
class TableSchema:
    def __init__(self, schema_name:str, schema_path:Path = Path("./") / os.path.dirname(__file__) / "TABLES/", is_legacy:bool = False):
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
        self._table_format_name : str                  = schema_name
        # self._is_legacy         : bool                 = is_legacy
        self._columns           : List[Dict[str, str]] = []
        self._column_map        : Map                  = {}

        if not self._table_format_name.lower().endswith(".json"):
            self._table_format_name += ".json"
        schema = utils.loadJSONFile(filename=self._table_format_name, path=schema_path)

        # after loading the file, take the stuff we need and store.
        if schema is not None:
            self._columns = schema['columns']
            self._column_map = schema['column_map']
        else:
            utils.Logger.Log(f"Could not find event_data_complex schemas at {schema_path}{schema_name}", logging.ERROR)

    def ColumnNames(self) -> List[str]:
        """Function to get the names of all columns in the schema.

        :return: Names of each column in the schema.
        :rtype: List[str]
        """
        return [col['name'] for col in self._columns]

    def ColumnList(self) -> List[Dict[str,str]]:
        return list(self._columns)

    def Markdown(self) -> str:
        ret_val = "## Database Columns  \n\n"
        ret_val += "The individual columns recorded in the database for this game.  \n\n"
        # set up list of database columns
        column_list = [f"**{item['name']}** : *{item['type']}* - {item['readable']}, {item['desc']}  " for item in self._columns]
        ret_val += "\n".join(column_list)
        # set up info on what is mapped to each event entry
        ret_val += "\n\n## Event Object Elements  \n\n"
        ret_val += "The elements (member variables) of each Event object, available to programmers when writing feature extractors. The right-hand side shows which database column(s) are mapped to a given element.  \n\n"
        event_column_list = []
        for evt_col,row_col in self._column_map.items():
            if row_col is not None:
                if type(row_col) == list:
                    mapped_list = ", ".join([f"'*{item}*'" for item in row_col])
                    event_column_list.append(f"**{evt_col}** = Columns {mapped_list}  ") # figure out how to do one string foreach item in list.
                elif type(row_col) == str:
                    event_column_list.append(f"**{evt_col}** = Column '*{row_col}*'  ")
            else:
                event_column_list.append(f"**{evt_col}** = null  ")
        ret_val += "\n".join(event_column_list)
        return ret_val

    def RowToEvent(self, row: Tuple, concatenator:str = '.'):
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
        app_ver : Union[str,None]
        offset  : Union[int,None]
        uid     : Union[str,None]
        udata   : Union[Map,None]
        state   : Union[Map,None]
        index   : Union[int,None]

        column_names = self.ColumnNames()
        row_dict = {col_i_name : row[i].isoformat() if type(row[i]) == datetime else str(row[i]) for i,col_i_name in enumerate(column_names)}
        # 1) Get values from row mapped to Event ctor params. Wait to do event_data.
        #    If anything in the map was a list, concatenate vals from corresponding columns, and anything that wasn't, get val.
        params : Map = {}
        for key in self._column_map.keys():
            if key != 'event_data': # event_data is special case, handle separately.
                inner_vals = self._column_map[key]
                if inner_vals == None:
                    params[key] = None
                elif type(inner_vals) == list:
                    params[key] = concatenator.join([row_dict[inner_key] for inner_key in inner_vals])
                else:
                    params[key] = row_dict[inner_vals]
        # 2) Handle event_data parameter, a special case.
        #    For this case we've got to parse the json, and then fold in whatever other columns were desired.
        if type(self._column_map['event_data']) == list:
            # if we had a list of event_data columns, we need a merger, not a concatenation
            params['event_data'] = {}
            for i,col_name in enumerate(self._column_map['event_data']):
                val = TableSchema._parse(row_dict[col_name], self._columns[column_names.index(col_name)])
                params['event_data'].update(val if type(val) == dict else {col_name:val})
        else:
            col_name = self._column_map['event_data']
            params['event_data'] = TableSchema._parse(row_dict[col_name], self._columns[column_names.index(col_name)])
        # 3) Assign vals to our arg vars and pass to Event ctor.
        sess_id = params['session_id']
        app_id  = params['app_id']
        # TODO: go bac to isostring function; need 0-padding on ms first, though
        time    = datetime.strptime(params['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")
        ename   = params['event_name']
        edata   = params['event_data']
        app_ver = params['app_version']
        offset  = params['time_offset']
        uid     = params['user_id']
        udata   = params['user_data']
        state   = params['game_state']
        index   = params['event_sequence_index']

        if self._columns[0]['name'] == "event_name" and app_ver is None:
            if "app_version" in params['event_data']:
                app_ver = str(params['event_data']['app_version']['int_value'])
            else:
                app_ver = "0"
        return Event(session_id=sess_id, app_id=app_id, timestamp=time,
                     event_name=ename, event_data=edata,
                     app_version=app_ver, time_offset=offset, user_id=uid, user_data=udata,
                     game_state=state, event_sequence_index=index)

    @staticmethod
    def _parse(input:str, column_descriptor:Dict[str,str]) -> Any:
        if column_descriptor['type'] == 'str':
            return str(input)
        elif column_descriptor['type'] == 'int':
            return int(input)
        elif column_descriptor['type'] == 'float':
            return float(input)
        elif column_descriptor['type'] == 'datetime':
            return str(input)
        elif column_descriptor['type'] == 'json':
            if input != 'None': # watch out for nasty corner case.
                try:
                    return json.loads(str(input))
                except JSONDecodeError as err:
                    utils.Logger.toStdOut(f"Could not parse input '{input}' of type {type(input)} from column {column_descriptor['name']}, got the following error:\n{str(err)}", logging.WARN)
                    return {}
            else:
                return None
        elif column_descriptor['type'].startswith('enum'):
            # if the column is supposed to be an enum, for now we just stick with the string.
            return str(input)
    

    # # parse out complex data from json
    # col = event[game_table.complex_data_index]
    # try:
    #     # complex_data_parsed = json.loads(col.replace("'", "\"")) if (col is not None) else {"event_custom":row[game_table.event_index]}
    #     complex_data_parsed = json.loads(col) if (col is not None) else {"event_custom":event[game_table.event_index]}
    # except Exception as err:
    #     msg = f"When trying to parse {col}, get error\n{type(err)} {str(err)}"
    #     utils.Logger.toStdOut(msg, logging.ERROR)
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
