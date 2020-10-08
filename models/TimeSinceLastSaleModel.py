from typing import List, Optional, Dict, Any, Union, Tuple, Callable
from collections import defaultdict
from models.SequenceModel import SequenceModel
import datetime
import operator
from functools import partial

## @class TimeSinceEventTypesModel
# Returns the number of seconds since the last purchase a player made
# @param levels: Levels applicable for model

class TimeSinceLastSaleModel(SequenceModel):
    def __init__(self, levels: List[int] = []):
        '''
        @class MoneyAccumulationModel
        Returns the number of seconds since the last purchase a player made
        :param levels: Levels applicable for model
        '''
        super().__init__()

    def _eval(self, events: List[Dict[str, Any]], verbose: bool = False) -> Optional[int]:
        assert events
        now = datetime.datetime.now()
        for event in reversed(events):
            # tally money for selling stuff since most recent gamestate event
            if event["event_custom"] == 37:
                event_time = event["server_time"]
                if type(event_time) is str:
                    event_time = datetime.datetime.fromisoformat(event_time)
                return (now - event_time).seconds
        return None


    def __repr__(self):
        return f"TimeSinceLastSaleModel(levels={self._levels}, input_type={self._input_type})"


_comparison_str_to_func = {
    "lt": operator.lt,
    "<": operator.lt,
    "le": operator.le,
    "<=": operator.le,
    "eq": operator.eq,
    "==": operator.eq,
    "ne": operator.ne,
    "!=": operator.ne,
    "ge": operator.ge,
    ">=": operator.ge,
    "gt": operator.gt,
    ">": operator.gt,
    "in": lambda a,b: a in b,
    "notin": lambda a, b: a not in b,
}


def _base_filter(event, funcs_all):
    for keys, comparison_str, value in funcs_all:
        event_value = event
        for key in keys:
            # print(event_value, key)
            # print(type(event_value))
            event_value = event_value[key]
        comparison_func = _comparison_str_to_func[comparison_str]
        if not comparison_func(event_value, value):
            return False
    return True

def _chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]