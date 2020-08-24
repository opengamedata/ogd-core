from abc import ABC
from datetime import timedelta
from typing import List, Optional
import pandas as pd
from bisect import bisect_left
import numpy as np

_POP_ACHS = "exist group town city".split()
_FARM_ACHS = "farmer farmers farmtown megafarm".split()
_MONEY_ACHS = "paycheck thousandair stability riches".split()
_BLOOM_ACHS = "bloom bigbloom hugebloom massivebloom".split()
_REQ_TUTORIALS = "buy_food build_a_farm timewarp \
successful_harvest sell_food buy_fertilizer buy_livestock \
livestock poop rain".split()  # skip build_a_house - it comes at 0.0


def _get_sess_active_time_to_achievement_list(achs):
    return [f'sess_time_active_to_{a}_achievement' for a in achs]


def _get_sess_active_time_to_tutorial_list(tuts):
    return [f'sess_time_active_to_{t}_tutorial' for t in tuts]

def _get_quantiles(df, feats, filter_debug=True, filter_continue=True):
    filter_strings = []
    if filter_debug:
        filter_strings += ['(debug==0)']
    if filter_continue:
        filter_strings += ['(c==0)']
    if filter_strings:
        df = df.rename({"continue": "c"}, axis=1).query(' & '.join(filter_strings)).rename({"c": "continue"},
                                                                                           axis=1)
    df = df[feats].replace(0.0, pd.NA)
    df = df.quantile(np.arange(0, 1, .01))
    quantiles = df.to_dict('list')
    return quantiles


class FeatureQuantiles(object):

    def __init__(self, df):
        if type(df) is str:
            df = pd.read_csv(path, index_col='sessID')
        cols = df.select_dtypes(include="number").columns
        self._nocont_quantiles = FeatureQuantiles._get_quantiles(df, cols, filter_continue=True)
        self._withcont_quantiles = FeatureQuantiles._get_quantiles(df, cols, filter_continue=False)

    def get_quantile(self, feat, value, include_continues=False, verbose=True, lo_to_hi=True):
        quants = self._withcont_quantiles if include_continues else self._nocont_quantiles
        quantile = bisect_left(quants[feat], value)
        if verbose:
            compare_str = "higher" if lo_to_hi else "lower"
            continue_str = "(including continues)" if include_continues else ""
            print(
                f'A {feat} of {value} units is {compare_str} than {quantile}% (the {quantile} percentile is {quants[feat][quantile]}) of sessions{continue_str}.')
        return quantile


_featureQuantiles = FeatureQuantiles(
    r"C:\Users\johnm\Development\FieldDay\opengamedata\data\LAKELAND\LAKELAND_20200501_to_20200530_de56000_proc\LAKELAND_20200501_to_20200530\LAKELAND_20200501_to_20200530_de56000_proc.csv")


class FeatSeqPercent(object):
    def __init__(self, feature_sequence: List[str], time_feat: str = 'sess_time_active'):
        self._feature_sequence = feature_sequence
        self._time_feat = time_feat
        super().__init__()

    def calc(self, sess: dict, verbose: bool = False) -> Optional[float]:
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
        if type(cur_time) is timedelta:  # proc features give float, but cgi might give timedelta
            cur_time = cur_time.seconds

        percentile_if_next_feat_now = _featureQuantiles.get_quantile(next_feat, cur_time, verbose=verbose)

        return percentile_if_next_feat_now


class FarmAchSeqPercent(FeatSeqPercent):
    def __init__(self):
        use_feats = _get_sess_active_time_to_achievement_list(_FARM_ACHS)
        super().__init__(use_feats)


class BloomAchSeqPercent(FeatSeqPercent):
    def __init__(self):
        use_feats = _get_sess_active_time_to_achievement_list(_BLOOM_ACHS)
        super().__init__(use_feats)


class MoneyAchSeqPercent(FeatSeqPercent):
    def __init__(self):
        use_feats = _get_sess_active_time_to_achievement_list(_MONEY_ACHS)
        super().__init__(use_feats)


class PopAchSeqPercent(FeatSeqPercent):
    def __init__(self):
        use_feats = _get_sess_active_time_to_achievement_list(_POP_ACHS)
        super().__init__(use_feats)


class ReqTutSeqPercent(FeatSeqPercent):
    def __init__(self):
        use_feats = _get_sess_active_time_to_tutorial_list(_REQ_TUTORIALS)
        super().__init__(use_feats)


class FeatVelocity(object):
    def __init__(self, feat_list: List[str], time_feat='sess_time_active'):
        self._feat_list = feat_list
        self._time_feat = time_feat
        super().__init__()

    def calc(self, sess: dict, verbose: bool = False) -> Optional[float]:
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


class FarmAchVelocity(FeatVelocity):
    def __init__(self):
        use_feats = _get_sess_active_time_to_achievement_list(_FARM_ACHS)
        super().__init__(use_feats)


class BloomAchVelocity(FeatVelocity):
    def __init__(self):
        use_feats = _get_sess_active_time_to_achievement_list(_BLOOM_ACHS)
        super().__init__(use_feats)


class MoneyAchVelocity(FeatVelocity):
    def __init__(self):
        use_feats = _get_sess_active_time_to_achievement_list(_MONEY_ACHS)
        super().__init__(use_feats)


class PopAchVelocity(FeatVelocity):
    def __init__(self):
        use_feats = _get_sess_active_time_to_achievement_list(_POP_ACHS)
        super().__init__(use_feats)


class ReqTutVelocity(FeatVelocity):
    def __init__(self):
        use_feats = _get_sess_active_time_to_tutorial_list(_REQ_TUTORIALS)
        super().__init__(use_feats)





