import abc
import typing
import logging
from abc import ABC
from statistics import median
import pandas as pd
import numpy as np
import json
from datetime import datetime as dt
## import local libraries
from models.SequenceModel import SequenceModel
from models.DeathPredModel import DeathPredModel

EMOTE_DESPERATE_ENUM = 2
FB_DEATH_ENUM = 18
EMOTE_EVT_ENUM = 24
MONEY_RATE_ENUM = 33
FOOD_AV_ENUM = 32
ACHIEV_ENUM = 17

class DeathThresholdModel(DeathPredModel):
    def __init__(self, levels=[]):
        super().__init__()
        self.thresh_df = pd.DataFrame()
        self.res_df = pd.DataFrame()

    def Eval(self, rows):
        return self._eval(rows)

    def _eval(self, rows):
        self.df = pd.DataFrame.from_records(rows)
        self.process_df()
        return self.matcher()

    def matcher(self):
        self.process_thresh_df()
        i_df = self.link_deaths_yums()
        i_df = i_df.merge(
            self.get_money_food_data(i_df), right_on='key', left_on=i_df.index, how='left')
        self.output_thresh_data(i_df)
        return self.res_df

    def process_thresh_df(self):
        self.filtered_df['key'] = self.filtered_df[['sess_id', 'name', 'event_custom', 'emote_enum']].apply(
            lambda x: self.f(*x), axis=1
        )
        self.filtered_df['fb_n'] = self.filtered_df['sess_id'].apply(
            lambda x: self.f2(x)
        )
        self.filtered_df['unique_keys_n'] = self.filtered_df[['sess_id', 'key']].apply(
            lambda x: self.f3(*x), axis=1
        )
        self.thresh_df = self.filtered_df.sort_values(
            by=['sess_id', 'utc_time_secs', 'key', 'event_custom'], ascending=[True, True, True, False])

        self.thresh_df = self.thresh_df.drop(
            list(self.thresh_df[self.thresh_df['unique_keys_n'] < 2].index), axis=0)
        # drop rows with only one key event

    def link_deaths_yums(self):
        t_df, i_df = self.thresh_df, pd.DataFrame()
        d_list = [x for x in t_df.itertuples() if x.event_custom == 24 and x.emote_enum == 2]
        for i in range(len(d_list)):
            # & (t_df['key']!=x.key)
            x = d_list[i]
            s = t_df[
                (t_df['sess_id'] == x.sess_id) &
                (t_df['utc_time_secs'] > x.utc_time_secs) &
                (t_df['name'] == x.name) &
                (t_df['key'] != x.key)].sort_values(by=['utc_time_secs'])
            el_dict = {
                "sess_id": x.sess_id, "h_key": x.key, "h_time": x.utc_time_secs, "fb": x.name, "fb_n": x.fb_n}
            if len(s.index) > 0:
                el = s.iloc[0, :]
                if el.key == x.key:
                    el = s.iloc[1, :]

                if el.event_custom == 24:
                    if el.emote_enum == 7:
                        el_dict['y_key'], el_dict['y_time'] = el.key, el.utc_time_secs
                        i_df = i_df.append(el_dict, ignore_index=True)
                    else:
                        raise Exception('code not filtering out desperates')
                elif el.event_custom == 18:
                    el_dict['d_key'], el_dict['d_time'] = el.key, el.utc_time_secs
                    i_df = i_df.append(el_dict, ignore_index=True)
                else:
                    raise Exception('random event detected')

        i_df = i_df.fillna(value={"y_key": "None", "d_key": "None", "y_time": -1, "d_time": -1})
        return i_df

    def get_money_food_data(self, i_df):
        food_money_df = pd.DataFrame()
        for x in i_df.itertuples():
            query = f'((sess_id == {x.sess_id}) & (event_custom == {FOOD_AV_ENUM}) | (event_custom == {MONEY_RATE_ENUM}))'
            if x.d_key == "None":
                query += f' & ((utc_time_secs > {x.h_time}) & (utc_time_secs < {x.y_time}))'
            elif x.y_key == "None":
                query += f' & ((utc_time_secs > {x.h_time}) & (utc_time_secs < {x.d_time}))'
            else:
                raise Exception("BOTH NONE?")
            s = self.df.query(query)
            fm_df = pd.DataFrame(
                list(s['event_data_complex'].values))
            fm_df['key'] = x.Index
            fm_df = fm_df.fillna(0)
            fm_df = fm_df.drop_duplicates()
            food_money_df = food_money_df.append(fm_df, ignore_index=True, sort=False)
        return self.money_food_thresh_data(food_money_df, i_df)

    def money_food_thresh_data(self, food_money_df, i_df):
        thresh_f = pd.DataFrame()
        for i, x in enumerate(i_df.itertuples()):
            fm_df, curr_fb = food_money_df.query(f'(key) == {i}'), 0
            money = sum([y.rate for y in fm_df.itertuples() if y.event_custom == 33])
            food = sum([y.food for y in fm_df.itertuples() if y.event_custom == 32])
            v_time = x.y_time if x.y_key != "None" else x.d_time
            gs_df = self.df.query(f'(event_custom == {0}) & (utc_time_secs < {v_time}) & (utc_time_secs > {x.h_time})')
            if len(gs_df.index) > 0:
                curr_fb_list = list(set(gs_df['event_data_complex'].apply(lambda x: self.f5(x), axis=1)))
                if len(curr_fb_list) == 1:
                    if curr_fb_list[0] < 1:
                        curr_fb = x.fb_n
                    else:
                        curr_fb = curr_fb_list[0]
                elif max(curr_fb_list) < 1:
                    curr_fb = x.fb_n
                else:
                    curr_fb = max(curr_fb_list)
            thresh_f = thresh_f.append({
                "key": x.Index,
                "avg_money": money / (curr_fb or 1),
                "avg_food": food / (curr_fb or 1),
                "total_money": money,
                "total_food": food,
                "interval_secs": v_time - x.h_time,
                "curr_fb_n": curr_fb
            }, ignore_index=True)

        return thresh_f

    def output_thresh_data(self, i_df):
        th_df = pd.DataFrame()
        for x in list(i_df['curr_fb_n'].drop_duplicates()):
            food_y = [r.total_food for r in i_df[i_df['curr_fb_n'] == x].itertuples() if r.y_key != "None"] + [0]
            food_d = [r.total_food for r in i_df[i_df['curr_fb_n'] == x].itertuples() if r.d_key != "None"] + [0]
            money_y = [r.total_money for r in i_df[i_df['curr_fb_n'] == x].itertuples() if r.y_key != "None"] + [0]
            money_d = [r.total_money for r in i_df[i_df['curr_fb_n'] == x].itertuples() if r.d_key != "None"] + [0]
            interval_y = [r.interval_secs for r in i_df[i_df['curr_fb_n'] == x].itertuples() if r.y_key != "None"] + [0]
            interval_d = [r.interval_secs for r in i_df[i_df['curr_fb_n'] == x].itertuples() if r.d_key != "None"] + [0]
            th_df = th_df.append(
                {
                    "fb_num": x, "max_food_to_yum": max(food_y),
                    "min_food_to_yum": min(food_y), "max_food_to_death": max(food_d),
                    "min_food_to_death": min(food_d), "max_money_to_yum": max(money_y),
                    "min_money_to_yum": min(money_y), "max_money_to_death": max(money_d),
                    "min_money_to_death": min(money_d), "avg_food_to_yum": sum(food_y) / len(food_y),
                    "avg_food_to_death": sum(food_d) / len(food_d), "avg_money_to_yum": sum(money_y) / len(money_y),
                    "avg_money_to_death": sum(money_d) / len(money_d),
                    "avg_interval_to_death": sum(interval_d) / len(interval_d),
                    "max_interval_to_death": max(interval_d), "min_interval_to_death": min(interval_d),
                    "avg_interval_to_yum": sum(interval_y) / len(interval_y), "max_interval_to_yum": max(interval_y),
                    "min_interval_to_yum": min(interval_y), "median_food_to_yum": median(food_y),
                    "median_food_to_death": median(food_d), "median_money_to_death": median(money_d),
                    "median_money_to_yum": median(money_y),
                }, ignore_index=True)
        self.res_df = th_df.sort_values(by=['fb_num']).set_index('fb_num')

    def f(self, s, n, v, e):
        if v == 24:
            return f'{int(n)}_{int(v)}_{int(e)}'
        else:
            return f'{int(n)}_{int(v)}'

    def f2(self, x):
        return len(
            self.filtered_df[self.filtered_df['sess_id'] == x]['name'].drop_duplicates())

    def f3(self, x, y):
        return len(
            self.filtered_df[(self.filtered_df['sess_id'] == x)]['key'].drop_duplicates().index
        )

    def read_stringified_array(self, arr: str):
        if not arr:
            return []
        return [int(x) for x in arr.split(',')]

    def f5(self, x):
        return len(self.read_stringified_array(x['farmbits'])) / 9