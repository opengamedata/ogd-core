from typing import List
from statistics import median
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
