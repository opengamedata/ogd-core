## import standard libraries
import abc
import typing
import logging
import pandas as pd
import numpy as np
import json
from datetime import datetime as dt
## import local libraries
from models.SequenceModel import SequenceModel

EMOTE_DESPERATE_FULL_ENUM = 2
FBDEATH_ENUM = 18
EMOTE_ENUM = 24
MONEYRATE_ENUM = 33
FOODRATE_ENUM = 34

class SimpleDeathPredictionModel(SequenceModel):
    def __init__(self, levels: typing.List[int] = [], time_int: int = 404):
        super().__init__(levels)
        self.levels = levels
        self.time_int = time_int
        self.df_filter = ['app_id', 'app_id_fast', 'player_id', 'app_version',
                          'persistent_sess_id', 'event', 'event_data_simple',
                          'server_time', 'remote_addr', 'req_id']
        self.farmBits = {}
        self.df = pd.DataFrame()
    ## Abstract declaration of a function to perform calculation of a model results from a row.
    #
    #  @param rows : A row of data for a session, which should be a mapping of column names to
    #  @return     : A result for the given row of data

    def Eval(self, rows: typing.List) -> typing.List:
        return self._eval(rows)

    def _eval(self, rows: typing.List):
        self.df = pd.from_records(rows)
        self.session_id = self.df.loc[0]['sess_id']
        self.processDF()
        self.sessEval(self.session_id)

        for fb in self.farmBits.values():
            if fb.getInt() > self.time_int:
                fb.printFarmBit()
                return False
        return True

    def processDF(self):
        if set(self.df_filter).issubset(set(self.df.columns)):
            self.df = self.df.drop(columns=self.df_filter, axis=0)
            self.df['utc_time_secs'] = self.df['client_time'].apply(
                lambda x: dt.fromisoformat(x).timestamp()
            )
            self.df['event_data_complex'] = self.df['event_data_complex'].apply(
                lambda x: json.loads(x)
            )
        self.hunger_df = self.processHungerDF()
        # (self.df['farmbit'], self.df['grave'], self.df['emote_enum']) = (
        #     self.srsExtract(self.df['event_data_complex'])
        # )
        # self.df = self.df.drop(index=list(
        #     self.df.query(
        #         '((emote_enum != 2) & (emote_enum != 0))').index), axis=1)

    def sessEval(self):
        for i, x in enumerate(self.df.itertuples()):
            if x.event_custom == EMOTE_DESPERATE_FULL_ENUM:
                self.farmBits[f'{sess}_{x.farmbit[2]}'] = self.farmBitDeaths(x)
            elif f'{sess}_{x.farmbit[2]}' not in self.farmBits.keys():
                raise Exception(
                    f'Farmbit {x.farmbit[2]} died without getting hungry. There\'s a bug, honey')
            else:
                self.farmBits[f'{sess}_{x.farmbit[2]}'].setDh(x)

    def srsExtract(self, series):
        a, b, c = [], [], []
        for el in list(series):
            x, y, z = self.extractDataEvents(el)
            a.append(x), b.append(y), c.append(z)
        return a, b, c

    def extractDataEvents(self, el):
        vals = list(el.values())
        x = vals[0]
        if "grave" in el.keys():    y, z = vals[1], 0
        else:   z, y = vals[1], 0
        return x, y, z

    def getFarmbitData(self, x):
        return {
            "fb_name": x.name,
            "hg_dh_interval_secs": x.getInt(),
            "session_id": x.session_id,
            "hg_data": x.hunger_data,
            "dh_data": x.death_data,
        }

    


class farmBitDeaths():
    def __init__(self, hunger_data, death_data=None):
        self.hunger_data = hunger_data
        self.name = self.hunger_data.event_data_complex['farmbit'][2]
        self.ht_time = self.hunger_data.utc_time_secs
        self.dh_time = -100000000
        self.session_id = self.hunger_data.sess_id
        self.death_data = 'No death' if death_data is None else death_data

    def setDh(self, death_data):
        self.death_data = death_data
        self.dh_time = self.death_data.utc_time_secs

    def getInt(self):
        if self.dh_time < 0:
            return self.dh_time
        return self.dh_time - self.ht_time

    def printFarmBit(self):
        s = f'Name: {self.name}\nTime:{self.getInt()}\nSession:{self.session_id}\n'
        s += f'Hunger: {self.hunger_data}\nDeath: {self.death_data}'
        print(s)