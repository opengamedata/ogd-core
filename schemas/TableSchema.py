## import standard libraries
from datetime import datetime
import json
import os
import logging
import typing
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
    def __init__(self, schema_name:str, schema_path:str = os.path.dirname(__file__) + "/TABLES/", is_legacy:bool = False):
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
        self._is_legacy         : bool                 = is_legacy
        self._columns           : List[Dict[str, str]] = []
        self._map               : Map                  = {}

        if not schema_name.lower().endswith(".json"):
            schema_name += ".json"
        schema = utils.loadJSONFile(schema_name, schema_path)

        # after loading the file, take the stuff we need and store.
        if schema is not None:
            self._columns = schema['columns']
            self._map = schema['map']
            # Take note of specific indices which will be useful when using a TableSchema
            # self.app_version_index:    int = self.column_names.index("app_version")
            # self.complex_data_index:   int = self.column_names.index("event_data_complex")
            # self.remote_addr_index:    int = self.column_names.index("remote_addr")
            # self.client_time_index:    int = self.column_names.index("client_time")
            # self.session_id_index:     int = self.column_names.index("session_id")
            # self.event_index:          int = self.column_names.index("event")
            # self.level_index:          int = self.column_names.index("level")
            # self.client_time_ms_index: int = self.column_names.index("client_time_ms")
            # self.server_time_index:    int = self.column_names.index("server_time")
            # self.pers_session_id_index:int = self.column_names.index("persistent_session_id")
            # self.event_custom_index:   int = self.column_names.index("event_custom")
            # self.version_index:        int = self.column_names.index("app_version")
            # self.player_id_index:      int = self.column_names.index("player_id")
            # utils.Logger.toStdOut("session_ids: " + str(session_ids), logging.DEBUG)
        else:
            utils.Logger.Log(f"Could not find event_data_complex schemas at {schema_path}{schema_name}", logging.ERROR)

    def RowToEvent(self, row: Tuple[str]):
        row_dict = self.RowToDict(row)
        # define vars to be passed as params
        sess_id : int
        app_id  : str
        time    : datetime
        ename   : str
        edata   : Map
        app_ver : Union[int,None] = None
        offset  : Union[int,None] = None
        uid     : Union[int,None] = None
        udata   : Union[Map,None] = None
        state   : Union[Map,None] = None
        index   : Union[int,None] = None

        # first, if anything in the map was a list, concatenate, and anything that wasn't, get val.
        params = {}
        for key in self._map.keys():
            if key != 'event_data': # event_data is special case, handle separately.
                inner_keys = self._map[key]
                if type(inner_keys) == list:
                    params[key] = '.'.join(row_dict[inner_key] for inner_key in inner_keys)
                else:
                    params[key] = row_dict[inner_keys]
        # second, handle special case of event data, where we've got to parse the json and then fold in whatever other columns were desired.
        if type(self._map['event_data']) == list:
            # if we had a list of event_data columns, we need a merger, not a concatenation
            for inner_key in self._map['event_data']:
                params['event_data'][inner_key] = row_dict[inner_key]
        else:
            params['event_data'] = row_dict[self._map['event_data']]
            if type(params['event_data']) == str:
                params['event_data'] = json.loads(params['event_data']) # we made sure to save this for last, because we need to parse 
        # second, find out which of our params were in the map, and assign vals to our vars.
        sess_id = int(params['session_id'])
        app_id  = params['app_id']
        time    = datetime.fromisoformat(params['timestamp'])
        ename   = params['event_name']
        edata   = 

        return Event(session_id=sess_id, app_id=app_id, timestamp=time,
                     event_name=params['event_name'], event_data=params['event_data'],
                     app_version=params, time_offset=offset, user_id=uid, user_data=udata,
                     game_state=state, event_sequence_index=index)

    ## Simple utility function to turn a raw row from the file/database into a dictionary,
    #  indexed with the column names retrieved from the file/database.
    def RowToDict(self, row):
        """Create Dict from a Row

        Args:
            row ([type]): [description]

        Returns:
            [type]: [description]
        """
        column_names = [col['name'] for col in self._columns]
        return {col_name : row[i] for i,col_name in enumerate(column_names)}