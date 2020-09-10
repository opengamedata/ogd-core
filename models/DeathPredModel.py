
## import standard libraries
import abc
import typing
import logging
from abc import ABC

import pandas as pd
import numpy as np
import json
from datetime import datetime as dt
## import local libraries
from models.SequenceModel import SequenceModel

EMOTE_DESPERATE_ENUM = 2
FB_DEATH_ENUM = 18
EMOTE_EVT_ENUM = 24
MONEY_RATE_ENUM = 33
FOOD_AV_ENUM = 32
ACHIEV_ENUM = 17


class DeathPredModel(SequenceModel, ABC):
    def __init__(self, levels: typing.List[int] = [], time_int: int = 404, food: int = 0, money: int = 0):
        super().__init__(levels)
        self.levels = levels
        self.time_int, self.food, self.money = time_int, food, money
        self.df_filter = ['app_id', 'app_id_fast', 'player_id', 'app_version',
                          'persistent_sess_id', 'event', 'event_data_simple',
                          'server_time', 'remote_addr', 'req_id']
        self.df, self.filtered_df = pd.DataFrame(), pd.DataFrame()
        self.farmBits = {}
        self.query = f'(event_custom == {FB_DEATH_ENUM}) | (event_custom == {EMOTE_EVT_ENUM})'

    ## Abstract declaration of a function to perform calculation of a model results from a row.
    #
    #  @param rows : A row of data for a session, which should be a mapping of column names to
    #  @return     : A result for the given row of data

    def all_hunger_death_eval(self):
        sessions = list(self.df['sess_id'].drop_duplicates())
        res = True
        for sess in sessions:
            self.hunger_death_sess_eval(sess)

    def food_money_death_eval(self, event: int):
        self.filtered_df = self.filtered_df.append(
            self.df.query(f'(event_custom == {event})'))
        (usr_val, cat) = (self.money, "money") if event == MONEY_RATE_ENUM else (self.food, "food")
        for x in self.farmBits.values():
            timeslice = self.filtered_df.query(
                f'(event_custom == {event}) & (utc_time_secs < {x.dh_time}) & (utc_time_secs > {x.hg_time})')
            if len(timeslice.index) > 0:
                for (key, data) in zip(timeslice['utc_time_secs'], timeslice['event_data_complex']):
                    if event == MONEY_RATE_ENUM:
                        x.money_data[key] = data
                    else:
                        x.food_data[key] = data

                    if data[cat] < usr_val: return False
        return True

    def hunger_death_sess_eval(self, sess: int):
        for i, x in enumerate(self.filtered_df[(self.filtered_df['sess_id'] == sess)].itertuples()):
            farmbit = x.event_data_complex['farmbit'][2]
            key = f'{sess}_{farmbit}'
            if x.event_custom == EMOTE_EVT_ENUM:
                self.farmBits[key] = self.FarmbitDeaths(x)
            elif key not in self.farmBits.keys():
                raise Exception(
                    f'Farmbit {farmbit} died without getting hungry. There\'s a bug, honey')
            else:
                self.farmBits[key].set_dh(x)

    def process_df(self):
        if set(self.df_filter).issubset(set(self.df.columns)):
            self.df = self.df.drop(columns=self.df_filter, axis=0)
            self.df['utc_time_secs'] = self.df['client_time'].apply(
                lambda x: dt.fromisoformat(x).timestamp())
            self.process_hunger_df()

    def process_hunger_df(self):
        self.filtered_df = self.df.query(self.query)
        drop_list = []
        for x in self.filtered_df[self.filtered_df.event_custom == EMOTE_EVT_ENUM].itertuples():
            if x.event_data_complex['emote_enum'] != EMOTE_DESPERATE_ENUM:
                drop_list.append(x.Index)

        return self.filtered_df.drop(index=drop_list, axis=0)

    def get_farmbit_data(self, x):
        return {
            "fb_name": x.name,
            "hg_dh_interval_secs": x.get_interval(),
            "session_id": x.session_id,
            "hg_data": x.hunger_data,
            "dh_data": x.death_data}

    def fb_to_csv(self, out):
        fb_df = pd.DataFrame()
        fb_df = fb_df.append([self.get_farmbit_data(x) for x in self.farmBits.values()], ignore_index=True)
        print(fb_df)
        fb_df.to_csv(out)

    class FarmbitDeaths():
        def __init__(self, hunger_data, death_data=None):
            self.hunger_data, self.dh_data = hunger_data, np.NaN
            self.name = self.hunger_data.event_data_complex['farmbit'][2]
            self.food_data, self.money_data = {}, {}
            self.hg_time, self.dh_time = self.hunger_data.utc_time_secs, -100000000
            self.session_id = self.hunger_data.sess_id

        def set_dh(self, death_data):
            self.dh_data = death_data
            self.dh_time = self.dh_data.utc_time_secs

        def get_interval(self):
            if self.dh_time < 0:
                return -self.dh_time
            return self.dh_time - self.hg_time

        def get_food(self):
            return sorted([[k, v['food']] for k, v in self.food_data.items()], key=lambda x: x[0])

        def get_money(self):
            return sorted([[k, v['money']] for k, v in self.money_data.items()], key=lambda x: x[0])

        def print_farmbit(self):
            dh_t_print = self.dh_data if self.dh_data == 'No death' else self.dh_data.utc_time_secs
            s = f'Name: {self.name}\nTime:{self.get_interval()}\nSession:{self.session_id}\n'
            s += f'Hunger: {self.hunger_data.utc_time_secs}\nDeath: {dh_t_print}\n'
            s += "\n".join(f'Session: {x[0]} Food: {x[1]}' for x in self.get_food()) + "\n"
            s += "\n".join(f'Session: {x[0]} Money: {x[1]}' for x in self.get_money())
            print(s)


class SimpleDeathPredModel(DeathPredModel):
    def __init__(self, levels = [], time_int=404):
        super().__init__(levels, time_int)

    def Eval(self, rows):
        return self._eval(rows)

    def _eval(self, rows):
        self.df = pd.DataFrame.from_records(rows)
        self.process_df()
        self.all_hunger_death_eval()
        if list(self.farmBits.values())[0].get_interval() > self.time_int:
            return False
        return True


class SimpleMoneyDeathPredModel(DeathPredModel):
    def __init__(self, levels=[], money=300):
        super().__init__(levels, money)

    def Eval(self, rows):

        return self._eval(rows)

    def _eval(self, rows):
        self.df = pd.DataFrame.from_records(rows)
        self.process_df()
        self.all_hunger_death_eval()
        return self.food_money_death_eval(MONEY_RATE_ENUM)


class SimpleFoodDeathPredModel(DeathPredModel):
    def __init__(self, levels=[], food=300):
        super().__init__(levels, food)

    def Eval(self, rows):

        return self._eval(rows)

    def _eval(self, rows):
        self.df = pd.DataFrame.from_records(rows)
        self.process_df()
        self.all_hunger_death_eval()
        return self.food_money_death_eval(FOOD_AV_ENUM)
