from typing import List, Optional, Dict, Any, Optional, Tuple, Callable
from collections import defaultdict
from models.SequenceModel import SequenceModel
import datetime
import operator
from functools import partial

# popular lakeland event lists

# _ACTIVE_EVENTS = ["SELECTTILE", "SELECTFARMBIT", "SELECTITEM", "SELECTBUY", "BUY",
#                   "CANCELBUY", "TILEUSESELECT", "ITEMUSESELECT", 'STARTGAME', 'TOGGLENUTRITION',
#                   "TOGGLESHOP", "TOGGLEACHIEVEMENTS", "SKIPTUTORIAL", "SPEED"]
# [3, 4, 5, 6, 7, 8, 10, 11, 1, 12, 13, 14, 15, 16]

# _EXPLORATORY_EVENTS = ['SELECTTILE', 'SELECTFARMBIT', 'SELECTITEM', 'TOGGLEACHIEVEMENTS', 'TOGGLESHOP',
#                        'TOGGLENUTRITION']
# [3, 4, 5, 14, 13, 12]


# _IMPACT_EVENTS = ["BUY", "TILEUSESELECT", "ITEMUSESELECT"]
# [7, 10, 11]

## @class TimeSinceEventTypesModel
# Returns time (in seconds) since last received an event from event_list, defaulting to time since first event if
# the given events have never been received.
# @param levels: Levels applicable for model
# @param event_list: events since which time is calculated (using any event, not all events)
# @param filters: A map from event enums to a list of lists. Each sublist represents a boolean function. Let f be a sublist.
# f[0] = event enum (no need to be distinct; a single enum can have multiple filters)
# f[1...-3] = keys and subkeys of an event
# f[-2] = "lt", "le", "eq", "ne", "ge", "gt", "in", or "notin"
# f[-1] = comparator value

class TimeSinceEventTypesModel(SequenceModel):
    def __init__(self, levels: List[int] = [], event_list: List[Any] = [0]):
        '''
        @class TimeSinceEventTypesModel
        Returns time (in seconds) since last received an event from event_list, defaulting to time since first event if
        the given events have never been received.
        :param levels: Levels applicable for model
        :param event_list: Either:
        List of integer events since which time is calculated (using any event, not all events) and
        lists of enum followed by filter arguments.
        Filter arguments are a list of lists. Each sublist represents a boolean function. Let f be a sublist.
        f[3n] = keys and subkeys of an event
        f[3n+1] = "lt", "le", "eq", "ne", "ge", "gt", or "in"
        f[3n+2] = comparator value
        Within a sublist, functions ALL have to return true. Outside a sublist, ANY can return true.

        Example:
        event_list = [
            1,
            2,
            [ 3, [
            [["event_data_complex", "buy"], "eq", 2],
            [["event_data_complex", "worth"], ">", 400]
            ]],
            [ 3 [
            [["event_data_complex", "buy"], "eq", 6],
            [["event_data_complex", "type"], "notin", ["farm", "livestock"]]
            ]]
        ]
        Would return the time since an event matching:
        event_custom==1 OR
        event_custom==2 OR
        (event_custom==3 AND buy==2 AND worth>400) OR
        (event_custom==3 AND buy==6 AND type not in ["farm", "livestock"])
        and defaults to the first event if none found.

        Example:
      "event_list": [
        [7, [
          [["event_data_complex", "buy"], "in", [1,3,5]],
          [["event_data_complex", "success"], "eq", true]
        ]]
      ]
        Would match any event_custom==7 (buy) where buy==1 (house), buy==3 (farm), or buy==5 (dairy), and the buy was a
        success. It would return the time since the most recent matching event in seconds.

        '''

        self._event_list = event_list
        self._parsed_filters = defaultdict(lambda: [])
        for event in event_list:
            if type(event) is int: # no filter
                self._parsed_filters[event].append(lambda event: True)
            else: # should be a 2-el list where the second element is a list of bool func lists
                event_enum, bool_funcs_all = event
                parsed_filter = partial(_base_filter, funcs_all=bool_funcs_all)
                self._parsed_filters[event_enum].append(parsed_filter)

        super().__init__()

    def _eval(self, events: List[Dict[str, Any]], verbose: bool = False) -> Optional[float]:
        if not events:
            return None
        now = events[-1]["client_time"] # assume this script in the same timezone as server, and server exports
        for event in reversed(events):
            event_filters = self._parsed_filters[event["event_custom"]]
            # if event_filters:
            #     print(event)
            if any(f(event) for f in event_filters):
                break

        event_time = event["client_time"]
        if type(event_time) is str: # fix for tests, datetimes don't always get parsed ahead of time
            event_time = datetime.datetime.fromisoformat(event_time)
        if type(now) is str:
            now = datetime.datetime.fromisoformat(now)
        return (now - event_time).total_seconds()


    def __repr__(self):
        return f"TimeSinceEventTypesModel(event_list={self._event_list},"\
               f", levels={self._levels}, input_type={self._input_type})"


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



