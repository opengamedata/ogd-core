from typing import List, Optional, Dict, Any
import pandas as pd
from datetime import datetime as dt
import json
from models.SequenceModel import SequenceModel

GAMESTATE_EVT = 0
BUY_EVT = 7
FARMFAIL_EVT = 25
FARMGROWTH_EVT = 41
BUY_FERT_EVT = 4
BUY_FARM_EVT = 3
TILE_TYPE_FARM = 9

log_type_dict = {
    GAMESTATE_EVT: "gamestate",
    BUY_EVT: "fertilizer",
    FARMFAIL_EVT: "farmfail",
    FARMGROWTH_EVT: "farmgrowth"
}

## @class SimpleFarmAbandonmentModel
# Returns a dictionary of farms abandoned and amount of time it is abandoned
# @param levels: Levels applicable for model

class SimpleFarmAbandonmentModel(SequenceModel):
    def __init__(self, levels: List[int] = []):
        super().__init__()

    def _eval(self, events: List[Dict[str, Any]], verbose: bool = False):
        self.df = pd.DataFrame.from_records(events)
        df_filter = ['app_id', 'app_id_fast', 'player_id', 'app_version',
                     'persistent_sess_id', 'event', 'event_data_simple',
                     'server_time', 'remote_addr', 'req_id', 'http_user_agent']
        if set(df_filter).issubset(set(self.df.columns)):
            self.df = self.df.drop(columns=df_filter, axis=0)
        self.df['utc_time_secs'] = pd.Series(self.df['client_time'].apply(
            lambda x: dt.fromisoformat(x).timestamp()), dtype=int)
        farm_fails = self.process_feature(FARMFAIL_EVT)
        return self.compose_results(self.add_time_abd(self.process_feature(BUY_EVT, False, BUY_FARM_EVT), farm_fails))

    def buy_filter(self, filt_type, args):
        res_filt = []
        if filt_type == BUY_EVT:
            for _ in self.df[self.df['event_custom'] == BUY_EVT].itertuples():
                if (_.event_data_complex['buy'] != args[1]) or not _.event_data_complex['success']:
                    res_filt.append(_.Index)
        return res_filt

    def feature_extract(self, evt):
        return self.df[self.df['event_custom'] == evt]

    def join_complex(self, frame):
        res_df = frame.join(
            pd.DataFrame(frame.event_data_complex.tolist(), index=frame.index),
            rsuffix='_complex')
        if 'utc_time_secs_complex' in list(res_df.columns):
            res_df = res_df.drop('utc_time_secs_complex', axis=1)
            'event_custom_complex'
        if 'event_custom_complex' in list(res_df.columns):
            res_df = res_df.drop('event_custom_complex', axis=1)
        return res_df

    def dict_tile(self, tile, farm_id):
        return {
            "val": tile[0],
            "nutrition": tile[1],
            "og_type": tile[2],
            "curr_type": tile[3],
            "tx": tile[4],
            "ty": tile[5],
            "farm_id": farm_id
        }

    def add_tiles(self, frame, is_gamestate=False):
        if len(frame.index) == 0:
            return frame

        if is_gamestate:
            # frame['tiles'] = frame['tiles'].apply(lambda x: compile_gs_tiles(x))
            pass
        else:
            frame['tile'] = frame['tile'].apply(lambda x: self.dict_tile(x, 0))
        return frame

    def process_feature(self, evt, is_gamestate=False, buy_item=0):
        if evt == BUY_EVT:
            return self.add_tiles(self.join_complex(self.feature_extract(evt).drop(
                self.buy_filter(BUY_EVT, ['buy', buy_item]), axis=0)))
        else:
            return self.add_tiles(self.join_complex(self.feature_extract(evt)), is_gamestate)

    def add_time_abd(self, frame, farmfails):
        time_abandoned = []
        for f in frame.itertuples():
            tx, ty, sess = f.tile['tx'], f.tile['ty'], f.sess_id
            fails = list(x for x in farmfails.itertuples() if
                         x.tile['tx'] == tx and x.tile['ty'] == ty and x.sess_id == sess)
            if len(fails) == 1:
                time_abandoned.append(fails[0].utc_time_secs - f.utc_time_secs)
            elif len(fails) > 1:
                time_abandoned.append(
                    max([fails[i].utc_time_secs - f.utc_time_secs for i in range(len(fails))]))
            else:
                time_abandoned.append(0)
        frame['time_abandoned'] = time_abandoned
        return frame

    def compose_results(self, frame):
        abd_ratio, avg_abd = {}, {}
        for sess in list(frame['sess_id'].drop_duplicates()):
            f_slice = list(frame[frame['sess_id'] == sess]['time_abandoned'].values)
            abd_ratio[sess] = sum([1 for x in f_slice if x > 0]) / (sum([1 for x in f_slice if x == 0]) or 1)
            avg_abd[sess] = sum(f_slice) / len(f_slice)

        frame['abd_ratio'] = [abd_ratio[x.sess_id] for x in frame.itertuples()]
        frame['avg_abd'] = [avg_abd[x.sess_id] for x in frame.itertuples()]
        if 'tile' not in frame.columns:
            return 'None abandoned' #might be something wrong here
        return frame[['sess_id', 'tile', 'utc_time_secs', 'time_abandoned', 'avg_abd', 'abd_ratio']]

