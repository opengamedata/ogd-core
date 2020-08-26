from abc import ABC
from typing import List, Optional
import pandas as pd
from bisect import bisect_left
import numpy as np
import os
import json
from datetime import timedelta
from models import FeatureModel

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
        df = df.rename({"continue": "c"}, axis=1).query(' & '.join(filter_strings)).rename({"c": "continue"}, axis=1)
    df = df[feats].replace(0.0, pd.NA)
    df = df.quantile(np.arange(0, 1, .01))
    quantiles = df.to_dict('list')
    return quantiles


class _FeatureQuantiles(object):

    def __init__(self, arg):
        if type(arg) is tuple:
            nocont, withcont = arg
            with open(nocont) as f:
                self._nocont_quantiles = json.load(f)
            with open(withcont) as f:
                self._withcont_quantiles = json.load(f)
            return

        df = arg
        cols = df.select_dtypes(include="number").columns
        self._nocont_quantiles = _get_quantiles(df, cols, filter_continue=True)
        self._withcont_quantiles = _get_quantiles(df, cols, filter_continue=False)

    @classmethod
    def fromDF(cls, df: pd.DataFrame) -> 'FeatureQuantiles':
        return cls(df)

    @classmethod
    def fromCSV(cls, csv_path: str) -> 'FeatureQuantiles':
        df = pd.read_csv(csv_path, index_col='sessID')
        return cls(df)

    @classmethod
    def fromJSONs(cls, no_continue_json_path: str, with_continue_json_path: str) -> 'FeatureQuantiles':
        return cls((no_continue_json_path, with_continue_json_path))

    def get_quantile(self, feat: str, value, include_continues: bool = False, verbose: bool = False,
                     lo_to_hi: bool = True) -> int:
        quants = self._withcont_quantiles if include_continues else self._nocont_quantiles
        quantile = bisect_left(quants[feat], value)
        if verbose:
            compare_str = "higher" if lo_to_hi else "lower"
            continue_str = " (including continues)" if include_continues else ""
            # print(quantile, len(quants[feat]))
            high_quant = quants[feat][quantile] if quantile < len(quants[feat]) else None
            low_quant = quants[feat][quantile - 1] if quantile > 0 else None
            quantile = quantile if lo_to_hi else 100 - quantile
            low_quant_offset = -1 if lo_to_hi else +1
            quant_low_str = f'{quantile + low_quant_offset}%={low_quant}'
            quant_high_str = f'{quantile}%={high_quant}'
            quant_str = f"{quant_low_str} and {quant_high_str}" if lo_to_hi else f"{quant_high_str} and {quant_low_str}"
            print(
                f'A {feat} of {value} units is {compare_str} than {quantile}% (between {quant_str}) of sessions{continue_str}.')
        return quantile

    def _export_quantiles(self, no_continue_json_path, with_continue_json_path):
        with open(no_continue_json_path, 'w+') as f:
            json.dump(self._nocont_quantiles, f, indent=4)
        with open(with_continue_json_path, 'w+') as f:
            json.dump(self._withcont_quantiles, f, indent=4)


_featureQuantiles = _FeatureQuantiles.fromJSONs(no_continue_json_path="lakeland_data\quantiles_no_continue.json",
                                               with_continue_json_path="lakeland_data\quantiles_with_continue.json")


class FeatSeqPercentModel(FeatureModel):
    def __init__(self, feature_sequence: List[str], levels: List[int] = [], time_feat: str = 'sess_time_active'):
        self._feature_sequence = feature_sequence
        self._time_feat = time_feat
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
        if type(cur_time) is timedelta:  # proc features give float, but cgi might give timedelta
            cur_time = cur_time.seconds

        percentile_if_next_feat_now = _featureQuantiles.get_quantile(next_feat, cur_time, verbose=verbose)

        return percentile_if_next_feat_now


class FarmAchSeqPercentModel(FeatSeqPercentModel):
    def __init__(self):
        use_feats = _get_sess_active_time_to_achievement_list(_FARM_ACHS)
        super().__init__(use_feats)


class BloomAchSeqPercentModel(FeatSeqPercentModel):
    def __init__(self):
        use_feats = _get_sess_active_time_to_achievement_list(_BLOOM_ACHS)
        super().__init__(use_feats)


class MoneyAchSeqPercentModel(FeatSeqPercentModel):
    def __init__(self):
        use_feats = _get_sess_active_time_to_achievement_list(_MONEY_ACHS)
        super().__init__(use_feats)


class PopAchSeqPercentModel(FeatSeqPercentModel):
    def __init__(self):
        use_feats = _get_sess_active_time_to_achievement_list(_POP_ACHS)
        super().__init__(use_feats)


class ReqTutSeqPercentModel(FeatSeqPercentModel):
    def __init__(self):
        use_feats = _get_sess_active_time_to_tutorial_list(_REQ_TUTORIALS)
        super().__init__(use_feats)


class FeatVelocityModel(FeatureModel):
    def __init__(self, feat_list: List[str], levels: List[int] = [], time_feat='sess_time_active'):
        self._feat_list = feat_list
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


class FarmAchVelocityModel(FeatVelocityModel):
    def __init__(self):
        use_feats = _get_sess_active_time_to_achievement_list(_FARM_ACHS)
        super().__init__(use_feats)


class BloomAchVelocityModel(FeatVelocityModel):
    def __init__(self):
        use_feats = _get_sess_active_time_to_achievement_list(_BLOOM_ACHS)
        super().__init__(use_feats)


class MoneyAchVelocityModel(FeatVelocityModel):
    def __init__(self):
        use_feats = _get_sess_active_time_to_achievement_list(_MONEY_ACHS)
        super().__init__(use_feats)


class PopAchVelocityModel(FeatVelocityModel):
    def __init__(self):
        use_feats = _get_sess_active_time_to_achievement_list(_POP_ACHS)
        super().__init__(use_feats)


class ReqTutVelocityModel(FeatVelocityModel):
    def __init__(self):
        use_feats = _get_sess_active_time_to_tutorial_list(_REQ_TUTORIALS)
        super().__init__(use_feats)





