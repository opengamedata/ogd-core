from typing import List, Optional, Dict, Any
import pandas as pd
from datetime import datetime as dt
import json
from models.SequenceModel import SequenceModel

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

    def _eval(self, events: List[Dict[str, Any]], verbose: bool = False):
        assert events
        df = pd.from_records(events)
        df_filter = ['app_id', 'app_id_fast', 'player_id', 'app_version',
                     'persistent_sess_id', 'event', 'event_data_simple',
                     'server_time', 'remote_addr', 'req_id', 'http_user_agent']
        df['utc_time_secs'] = pd.Series(df['client_time'].apply(
            lambda x: dt.fromisoformat(x).timestamp()), dtype=int)
        df['event_data_complex'] = df['event_data_complex'].apply(
            lambda x: json.loads(x))
        return self.get_res(df)

    def get_res(self, df):
        res_dict = {}
        now = dt.utcnow().timestamp()
        for x in df[df['utc_time_secs'] > now - self.time]:
            if x.event_custom in list(self._ACTIVE_EVENTS.keys()):
                if x.utc_time_secs > now - self.time:
                    event_val = f'{self._ACTIVE_EVENTS[x.event_custom]}_cnt'
                    if event_val not in res_dict:
                        res_dict[event_val] = 1
                    else:
                        res_dict[event_val] += 1
        res_dict['actions_per_secs'] = sum(res_dict.values) / self.time
        return res_dict
