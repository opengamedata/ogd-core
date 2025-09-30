from typing import List, Optional, Dict, Any
import pandas as pd
from datetime import datetime as dt
import json
from models.SequenceModel import SequenceModel

## @class ActionsLastXSecondsModel
# Returns a dictionary of active events for the last X seconds
# @param levels: Levels applicable for model, time: last x seconds
class ActionsLastXSecondsModel(SequenceModel):

    def __init__(self, time=30, levels: List[int] = []):
        '''
        @class MoneyAccumulationModel
        Returns a tuple with (1) the current amount of money and (2) the total number of homes,
        farms, and dairy farms
        :param levels: Levels applicable for model
        '''
        super().__init__()
        self.time = time
        self._ACTIVE_EVENTS = {3: "SELECTTILE", 4: "SELECTFARMBIT", 5: "SELECTITEM", 6: "SELECTBUY", 7: "BUY",
                          8: "CANCELBUY", 10: "TILEUSESELECT", 11: "ITEMUSESELECT", 1: 'STARTGAME',
                          12: 'TOGGLENUTRITION', 13: "TOGGLESHOP", 14: "TOGGLEACHIEVEMENTS",
                          15: "SKIPTUTORIAL", 16: "SPEED"}

    def get_utc(self, data):
        dt_string = '%Y-%m-%d %H:%M:%S'
        return dt.strptime(data, dt_string).timestamp()

    def _eval(self, events: List[Dict[str, Any]], verbose: bool = False):
        assert events
        return self.get_res(events)

    def get_res(self, events):
        res_dict = {}
        now = dt.utcnow().timestamp()
        for row in events:
            evt_time = self.get_utc(row['client_time'])
            if (evt_time > (now-self.time)) and (evt_time < now):
                if row['event_custom'] in self._ACTIVE_EVENTS.keys():
                    evt = self._ACTIVE_EVENTS[row['event_custom']]
                    event_val = f'{evt}_cnt'
                    if event_val not in res_dict:
                        res_dict[event_val] = 1
                    else:
                        res_dict[event_val] += 1
        res_dict['actions_per_secs'] = sum(res_dict.values()) / self.time
        return res_dict
