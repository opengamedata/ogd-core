from typing import List, Optional
from models.FeatureModel import FeatureModel
from datetime import timedelta

class FeatVelocityModel(FeatureModel):
    def __init__(self, feature_list: List[str], levels: List[int] = [], time_feat='sess_time_active'):
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
        if type(time) is timedelta:  # proc features give float, but cgi might give timedelta
            time = time.seconds

        return time / num_reached_feats