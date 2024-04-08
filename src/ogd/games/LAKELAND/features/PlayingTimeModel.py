from typing import List
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
from models.FeatureModel import FeatureModel


class PlayingTimeModel(FeatureModel):
    def __init__(self, features: List[str]):
        super().__init__()
        self._features = features

    def _eval(self, sess: dict, verbose: bool = False):
        res = {}
        if sess['continue'] or sess['debug']:
            return None
        for x in self._features:
            res[x] = sess[x]
        return res
