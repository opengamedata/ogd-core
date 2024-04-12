from typing import List
from statistics import median
from datetime import datetime as dt
## import local libraries
from models.FeatureModel import FeatureModel

## @class TutorialProgressionModel
# Returns dictionary of time of first pivotal tutorial events in the game
# @param levels: Levels applicable for model, tut_features: tutorial features

CHECKPOINT_EVT = 2
extract_firsts = dict(sess_time_to_first_home_buy="first_house", sess_time_to_sell_food_tutorial="first_sale",
                      sess_time_to_first_livestock_buy="first_livestock", sess_time_to_first_farm_buy="first_farm",
                      sess_time_to_first_fertilizer_buy="first_fertilizer",
                      sess_time_to_extra_life_tutorial="first_death_of_last_farmbit")


class TutorialProgressionModel(FeatureModel):
    def __init__(self, tut_features: List[str]):
        super().__init__()
        self._tut_features = tut_features

    def _eval(self, sess: dict, verbose: bool = False):
        res = {}
        if sess['continue'] or sess['debug']:
            return None
        for x in self._tut_features:
            res[x] = sess[x]
        return res
