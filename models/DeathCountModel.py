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

class DeathCountModel(DeathPredModel):
    def __init__(self, levels=[]):
        super().__init__()
        self.thresh_df = pd.DataFrame()
        self.res_df = pd.DataFrame()

    def Eval(self, rows):
        return self._eval(rows)

    def _eval(self, rows):
        self.df = pd.DataFrame.from_records(rows)
        self.process_df()
        return self.count()

    def count(self):
        return len(self.df[self.df['event_custom'] == FB_DEATH_ENUM].index)