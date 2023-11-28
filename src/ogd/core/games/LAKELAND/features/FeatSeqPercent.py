## @module FeatSeqPercentModel
# Feature to output the percentile that a session is at along a progression of gameplay timestamp features. Depends
# heavily on the logic used to produce the quantiles file. The following exemplifies current implementation:
#
# Example: A game has 10 checkpoints. Joey has reached 3/10 checkpoints. His total playtime so far is 45 seconds.
# The model will return the percentile of reaching checkpoint 4 at 45 seconds. If historically 70% of students take
# longer than 45 seconds to reach checkpoint 4, the model will return 30%.
#
# Example: A game has 10 checkpoints. Joey has reached 10/10 checkpoints. His total playtime so far is 190 seconds.
# He reached checkpoint 10 at 185 seconds. The model will return the percentile of reaching checkpoint 10 at 185
# seconds, and will continue returning that same value for this session.
#
# @param feature_sequence: sequence of timedelta features that are to be in strictly ascending order
# @param levels: levels applicable to this model
# @param time_feat: "sessDuration" or "sess_time_active", depending if the model should be used for active time or
# overall time. Make sure that the quantiles file uses the same time feature.
# @param quantile_json_path: Path to a quantiles JSON file constructed by the _FeatureQuantiles private class


from typing import List, Optional, Dict, Any
import pandas as pd
from bisect import bisect_left
import numpy as np
import json
from datetime import timedelta
from models.FeatureModel import FeatureModel
from ogd.core.utils.Logger import Logger

_POP_ACHS = "exist group town city".split()
_FARM_ACHS = "farmer farmers farmtown megafarm".split()
_MONEY_ACHS = "paycheck thousandair stability riches".split()
_BLOOM_ACHS = "bloom bigbloom hugebloom massivebloom".split()
_REQ_TUTORIALS = "buy_food build_a_farm timewarp \
successful_harvest sell_food buy_fertilizer buy_livestock \
livestock poop rain".split()  # skip build_a_house - it comes at 0.0


def _get_sess_active_time_to_achievement_list(achs: List[str]) -> List[str]:
    return [f'sess_time_active_to_{a}_achievement' for a in achs]


def _get_sess_active_time_to_tutorial_list(tuts: List[str]) -> List[str]:
    return [f'sess_time_active_to_{t}_tutorial' for t in tuts]


def _get_quantiles(df: pd.DataFrame, feats: List[str], filter_debug:bool=True, filter_continue:bool=True) -> Dict[str, List[float]]:
    filter_strings = []
    if filter_debug:
        filter_strings += ['(debug==0)']
    if filter_continue:
        filter_strings += ['(c==0)']
    if filter_strings:
        df = df.rename({"continue": "c"}, axis=1).query(' & '.join(filter_strings)).rename({"c": "continue"}, axis=1)
    df = df[feats].replace(0.0, pd.NA)
    df = df.quantile(np.arange(0, 1, .01))
    quantiles = df.to_dict('list')
    return quantiles

## @class _FeatureQuantiles
# A private class used to create singleton access to quantile data used by the FeatSeqPercentModel class.
class _FeatureQuantiles(object):

    def __init__(self, arg, filter_continue=True):
        if type(arg) is str:
            json_path = arg
            with open(json_path) as f:
                self._quantiles = json.load(f)
            return

        df = arg
        cols = df.select_dtypes(include="number").columns
        self._quantiles = _get_quantiles(df, cols, filter_continue=filter_continue)

    @classmethod
    def fromDF(cls, df: pd.DataFrame, filter_continue=True) -> 'FeatureQuantiles':
        return cls(df, filter_continue=filter_continue)

    @classmethod
    def fromCSV(cls, csv_path: str, filter_continue=True) -> 'FeatureQuantiles':
        df = pd.read_csv(csv_path, index_col='sessID')
        return cls(df, filter_continue=filter_continue)

    @classmethod
    def fromJSON(cls, quantile_json_path: str) -> 'FeatureQuantiles':
        return cls(quantile_json_path)

    def get_quantile(self, feat: str, value, verbose: bool = False,
                     lo_to_hi: bool = True) -> int:
        quantile = bisect_left(self._quantiles[feat], value)
        if verbose:
            compare_str = "higher" if lo_to_hi else "lower"
            # print(quantile, len(self._quantiles[feat]))
            high_quant = self._quantiles[feat][quantile] if quantile < len(self._quantiles[feat]) else None
            low_quant = self._quantiles[feat][quantile - 1] if quantile > 0 else None
            quantile = quantile if lo_to_hi else 100 - quantile
            low_quant_offset = -1 if lo_to_hi else +1
            quant_low_str = f'{quantile + low_quant_offset}%={low_quant}'
            quant_high_str = f'{quantile}%={high_quant}'
            quant_str = f"{quant_low_str} and {quant_high_str}" if lo_to_hi else f"{quant_high_str} and {quant_low_str}"
            Logger.Log(
                f'A {feat} of {value} units is {compare_str} than {quantile}% (between {quant_str}) of sessions.')
        return quantile

    def _export_quantiles(self, path):
        with open(path, 'w+') as f:
            json.dump(self._quantiles, f, indent=4)



## @class FeatSeqPercentModel
# Feature to output the percentile that a session is at along a progression of gameplay timestamp features. Depends
# heavily on the logic used to produce the quantiles file. The following exemplifies current implementation:
#
# Example: A game has 10 checkpoints. Joey has reached 3/10 checkpoints. His total playtime so far is 45 seconds.
# The model will return the percentile of reaching checkpoint 4 at 45 seconds. If historically 70% of students take
# longer than 45 seconds to reach checkpoint 4, the model will return 30%.
#
# Example: A game has 10 checkpoints. Joey has reached 10/10 checkpoints. His total playtime so far is 190 seconds.
# He reached checkpoint 10 at 185 seconds. The model will return the percentile of reaching checkpoint 10 at 185
# seconds, and will continue returning that same value for this session.
#
# @param feature_sequence: sequence of timedelta features that are to be in strictly ascending order
# @param levels: levels applicable to this model
# @param time_feat: "sessDuration" or "sess_time_active", depending if the model should be used for active time or
# overall time. Make sure that the quantiles file uses the same time feature.
# @param quantile_json_path: Path to a quantiles JSON file constructed by the _FeatureQuantiles private class

class FeatSeqPercentModel(FeatureModel):
    def __init__(self, feature_sequence: List[str], levels: List[int] = [], time_feat: str = 'sess_time_active',
                 quantile_json_path: str = "models/lakeland_data/quantiles_no_continue.json"):
        self._quantile_json_path = quantile_json_path
        self._feature_sequence = feature_sequence
        self._time_feat = time_feat
        self._featureQuantiles = _FeatureQuantiles.fromJSON(
            quantile_json_path=quantile_json_path)

        super().__init__()

    def _eval(self, sess: dict, verbose: bool = False) -> Optional[float]:
        if sess['continue'] or sess['debug']:
            return None
        time_to_vals = [sess[f] for f in self._feature_sequence]
        idx_next = sum(bool(v) for v in time_to_vals)
        if idx_next < len(self._feature_sequence):
            next_feat = self._feature_sequence[idx_next]
            cur_time = sess[self._time_feat]
        else:
            next_feat = self._feature_sequence[-1]
            cur_time = time_to_vals[-1]
        if type(cur_time) is timedelta:  # sessions features give float, but cgi might give timedelta
            cur_time = cur_time.total_seconds()

        percentile_if_next_feat_now = self._featureQuantiles.get_quantile(next_feat, cur_time, verbose=verbose)

        return percentile_if_next_feat_now

    def __repr__(self):
        return f"FeatSeqPercentModel(feature_sequence={self._feature_sequence}, time_feat='{self._time_feat}'" \
               f"quantile_json_path='{self._quantile_json_path}'" \
               f", levels={self._levels}, input_type={self._input_type})"


