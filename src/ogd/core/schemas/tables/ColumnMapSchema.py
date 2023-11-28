# import standard libraries
import logging
from typing import Any, Dict, List, Union
# import local files
from ogd.core.schemas.tables.ColumnSchema import ColumnSchema
from ogd.core.utils.Logger import Logger

class ColumnMapSchema:
    def __init__(self, map:Dict[str, Any], column_names:List[str]):
        self._map                  : Dict[str, Union[int, List[int], Dict[str,int], None]] = {
            "session_id"           : None,
            "app_id"               : None,
            "timestamp"            : None,
            "event_name"           : None,
            "event_data"           : None,
            "event_source"         : None,
            "app_version"          : None,
            "app_branch"           : None,
            "log_version"          : None,
            "time_offset"          : None,
            "user_id"              : None,
            "user_data"            : None,
            "game_state"           : None,
            "event_sequence_index" : None
        }
        self._other_elements       : Dict[str, Any]
        self._column_names = column_names

        if isinstance(map, dict):
            for key in self._map.keys():
                if key in map:
                    element = ColumnMapSchema._parseElement(elem=map[key], name=key)
                    if isinstance(element, str):
                        self._map[key] = column_names.index(element)
                    elif isinstance(element, list):
                        self._map[key] = [column_names.index(listelem) for listelem in element]
                    elif isinstance(element, dict):
                        self._map[key] = {key : column_names.index(listelem) for key,listelem in element.items()}
                else:
                    Logger.Log(f"Column config does not have a '{key}' element, defaulting to {key} : None", logging.WARN)
            self._other_elements = { key : val for key,val in map.items() if key not in self._map.keys() }
        else:
            self._other_elements = {}
            Logger.Log(f"For TableSchema config, map was not a dict, defaulting all items in map to None", logging.WARN)

    @property
    def Map(self) -> Dict[str, Union[int, List[int], Dict[str, int], None]]:
        """Mapping from Event element names to the indices of the database columns mapped to them.
        There may be a single index, indicating a 1-to-1 mapping of a database column to the element;
        There may be a list of indices, indicating multiple columns will be concatenated to form the element value;
        There may be a further mapping of keys to indicies, indicating multiple columns will be joined into a JSON object, with keys mapped to values found at the columns with given indices.

        :return: The dictionary mapping of element names to indices.
        :rtype: Dict[str, Union[int, List[int], Dict[str, int], None]]
        """
        return self._map

    @property
    def SessionID(self) -> Union[int, List[int], Dict[str, int], None]:
        return self._map['session_id']

    @property
    def AppID(self) -> Union[int, List[int], Dict[str, int], None]:
        return self._map['app_id']

    @property
    def Timestamp(self) -> Union[int, List[int], Dict[str, int], None]:
        return self._map['timestamp']

    @property
    def EventName(self) -> Union[int, List[int], Dict[str, int], None]:
        return self._map['event_name']

    @property
    def EventData(self) -> Union[int, List[int], Dict[str, int], None]:
        return self._map['event_data']

    @property
    def EventSource(self) -> Union[int, List[int], Dict[str, int], None]:
        return self._map['event_source']

    @property
    def AppVersion(self) -> Union[int, List[int], Dict[str, int], None]:
        return self._map['app_version']

    @property
    def AppBranch(self) -> Union[int, List[int], Dict[str, int], None]:
        return self._map['app_branch']

    @property
    def LogVersion(self) -> Union[int, List[int], Dict[str, int], None]:
        return self._map['log_version']

    @property
    def TimeOffset(self) -> Union[int, List[int], Dict[str, int], None]:
        return self._map['time_offset']

    @property
    def UserID(self) -> Union[int, List[int], Dict[str, int], None]:
        return self._map['user_id']

    @property
    def UserData(self) -> Union[int, List[int], Dict[str, int], None]:
        return self._map['user_data']

    @property
    def GameState(self) -> Union[int, List[int], Dict[str, int], None]:
        return self._map['game_state']

    @property
    def EventSequenceIndex(self) -> Union[int, List[int], Dict[str, int], None]:
        return self._map['event_sequence_index']

    @property
    def Elements(self) -> Dict[str, str]:
        return self._other_elements

    @property
    def ElementNames(self) -> List[str]:
        return list(self._other_elements.keys())

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        event_column_list = []
        for evt_col,row_col in self._map.items():
            if row_col is not None:
                if isinstance(row_col, str):
                    event_column_list.append(f"**{evt_col}** = Column '*{row_col}*'  ")
                elif isinstance(row_col, list):
                    mapped_list = ", ".join([f"'*{item}*'" for item in row_col])
                    event_column_list.append(f"**{evt_col}** = Columns {mapped_list}  ") # figure out how to do one string foreach item in list.
                elif isinstance(row_col, int):
                    event_column_list.append(f"**{evt_col}** = Column '*{self._column_names[row_col]}*' (index {row_col})  ")
                else:
                    event_column_list.append(f"**{evt_col}** = Column '*{row_col}*' (DEBUG: Type {type(row_col)})  ")
            else:
                event_column_list.append(f"**{evt_col}** = null  ")
        ret_val = "\n".join(event_column_list)
        return ret_val
    
    @staticmethod
    def _parseElement(elem:Any, name:str) -> Union[str, List[str], Dict[str, str], None]:
        ret_val : Union[str, List[str], Dict[str, str], None]
        if elem is not None:
            if isinstance(elem, str):
                ret_val = elem
            elif isinstance(elem, list):
                ret_val = elem
            elif isinstance(elem, dict):
                ret_val = elem
            else:
                ret_val = str(elem)
                Logger.Log(f"Column name(s) mapped to {name} was not a string or list, defaulting to str(name) == {ret_val} being mapped to {name}", logging.WARN)
        else:
            ret_val = None
            Logger.Log(f"Column name mapped to {name} was left null, nothing will be mapped to {name}", logging.WARN)
        return ret_val
