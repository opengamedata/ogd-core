from typing import List, Optional, Dict, Any
from models.SequenceModel import SequenceModel
import datetime

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


class TimeSinceEventTypesModel(SequenceModel):
    def __init__(self, levels: List[int] = [], event_list: List[int] =[0]):
        self._event_list = set(event_list)
        super().__init__()

    def _eval(self, events: List[Dict[str, Any]], verbose: bool = False) -> int:
        assert events
        now = datetime.datetime.now() # assume this script in the same timezone as server, and server exports
        for event in events:
            if event["event_custom"] in self._event_list:
                break
        event_time = event["server_time"]
        if type(event_time) is str: # fix for tests, datetimes don't always get parsed ahead of time
            event_time = datetime.datetime.fromisoformat(event_time)
        return (now - event_time).seconds


    def __repr__(self):
        return f"TimeSinceEventTypesModel(event_list={self._event_list}" \
               f", levels={self._levels}, input_type={self._input_type})"
