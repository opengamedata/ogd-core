## @module
# Calculates number of checkpoint features in list achieved per 1000 seconds of gameplay time, given by time_feat.
# @param feature_list: list of features to use.
# @param levels: Levels to use this feature during
# @param time_feat: sessDuration" or "sess_time_active", depending if the model should be used for active time or
# overall time.


from typing import List, Optional
from models.FeatureModel import FeatureModel
from datetime import timedelta

## @class
# Calculates number of checkpoint features in list achieved per 1000 seconds of gameplay time, given by time_feat.
# @param feature_list: list of features to use.
# @param levels: Levels to use this feature during
# @param time_feat: sessDuration" or "sess_time_active", depending if the model should be used for active time or
# overall time.
class FeatVelocityModel(FeatureModel):
    def __init__(self, feature_list: List[str], levels: List[int] = [], time_feat='sess_time_active'):
        '''
        Calculates number of checkpoint features in list achieved per 1000 seconds of gameplay time, given by time_feat.
        :param feature_list: list of features to use.
        :param levels: Levels to use this feature during
        :param time_feat: sessDuration" or "sess_time_active", depending if the model should be used for active time or
        overall time.
        '''
        self._feat_list = feature_list
        self._time_feat = time_feat
        super().__init__()

    def _eval(self, sess: dict, verbose: bool = False) -> Optional[float]:
        if sess['continue'] or sess['debug']:
            return None
        time_to_vals = [sess[f] for f in self._feat_list]
        if not any(time_to_vals):
            return 0
        num_reached_feats = sum(bool(v) for v in time_to_vals)
        if all(time_to_vals):
            time = max(time_to_vals)
        else:
            time = sess[self._time_feat]
        if type(time) is timedelta:  # sessions features give float, but cgi might give timedelta
            time = time.total_seconds()

        return num_reached_feats / time * 1000


    def __repr__(self):
        return f"FeatVelocityModel(feature_list={self._feat_list}, time_feat='{self._time_feat}'" \
               f", levels={self._levels}, input_type={self._input_type})"
