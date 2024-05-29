## import standard libraries
import abc
import logging
import typing
import logging
from collections import defaultdict
from datetime import timedelta
from typing import Any, Dict, List, Optional, Union
## import local files
from ogd.core.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.schemas.games.GameSchema import GameSchema

LegacyFeatureType = Union[int,float,timedelta,Dict[int,Dict[str,Any]]]

## @class LegacyFeature
#  Abstract base class for game feature extractors.
#  Gives a few static functions to be used across all extractor classes,
#  and defines an interface that the SessionProcessor can use.
class LegacyFeature(Feature):

    # *** ABSTRACTS ***

    @abc.abstractmethod
    def _calculateAggregateFeatures(self) -> None:
        """Abstract declaration of a function to perform calculation of aggregate features
        from existing per-level/per-custom-count features.
        Will be called as a first step anytime GetFeatureValues is called.
        """
        return

    # *** BUILT-INS & PROPERTIES ***

    # Base constructor for LegacyFeature classes.
    def __init__(self, params:GeneratorParameters, game_schema:GameSchema, session_id:str):
        """Base constructor for LegacyFeature classes.
        The constructor sets an extractor's session id and range of levels,
        as well as initializing the features dictionary and list of played levels.

        :param session_id: The id of the session from which we will extract features.
        :type session_id: int
        :param game_schema: A dictionary that defines how the game data itself is structured
        :type game_schema: GameSchema
        """
        self._session_id  : str         = session_id
        self._game_schema : GameSchema  = game_schema
        self._levels      : List[int]   = []
        self._sequences   : List        = []
        self._features    : LegacyFeature.LegacySessionFeatures = LegacyFeature.LegacySessionFeatures(game_schema=game_schema)
        super().__init__(params=params)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["all_events"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        self._calculateAggregateFeatures()
        def _format(obj):
            if obj == None:
                return ""
            elif type(obj) is timedelta:
                total_secs = obj.total_seconds()
                # h = total_secs // 3600
                # m = (total_secs % 3600) // 60
                # s = (total_secs % 3600) % 60 // 1  # just for reference
                # return f"{h:02.0f}:{m:02.0f}:{s:02.3f}"
                return str(total_secs)
            if obj is None:
                return ''
            else:
                return str(obj)
        column_vals = []
        # TODO: Should we do anything if the user accidentally adds a feature? For example I accidentally was adding 2
        # features that weren't in the schema (by misreferencing actual features), and they were appended to the end of
        # the feature list.
        for key in self._features.FeatureNames:
            _feature = self._features.getValByName(feature_name=key)
            if _feature is not None:
                key_type = type(_feature)
                if key_type is type({}) or key_type is type(defaultdict()):
                    # if it's a dictionary, expand.
                    column_vals.extend([_format(self._features.getValByIndex(key, num)) for num in _feature.keys()])
                else:
                    column_vals.append(_format(self._features.getValByName(key)))
        return column_vals

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***


    def GetFeatureNames(self) -> List[str]:
        columns = []
        for feat_name,feat_content in self._features.Features.items():
            if type(feat_content) is dict:
                # if it's a dictionary, expand.
                columns.extend([f"{feat_content[num]['prefix']}{num}_{feat_name}" for num in feat_content.keys()])
            else:
                columns.append(str(feat_name))
        return columns


    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    ## @class LegacySessionFeatures
    #  Private LegacyFeature class to track feature data.
    #  This class provides several functions to manage data, which should make
    #  the actual extractor code easier to read/write, since there is less need
    #  to understand the structure of feature data.
    class LegacySessionFeatures:
        def __init__(self, game_schema: GameSchema):
            self._features       : Dict[str, LegacyFeatureType] = {}
            self._perlevel_names : List[str] = list(game_schema._legacy_perlevel_feats.keys())

            _perlevels = game_schema._legacy_perlevel_feats
            _level_range = range(game_schema._min_level   if game_schema._min_level is not None else 0,
                                 game_schema._max_level+1 if game_schema._max_level is not None else 1)
            self._features.update({f:{lvl:{"val":None, "prefix":"lvl"} for lvl in _level_range } for f in _perlevels.keys()})
            # next, do something similar for other per-custom-count features.
            _percounts = game_schema.PerCountFeatures
            self._features.update({f:{num:{"val":None, "prefix":_percounts[f].Prefix} for num in range(0, int(_percounts[f].Count)) } for f in _percounts.keys()})
            # finally, add in aggregate-only features.
            self._features.update({f:0 for f in game_schema.AggregateFeatures.keys()})

        @property
        def Features(self):
            return self._features

        ## Getter function to retrieve a list of all features in the LegacySessionFeatures dictionary.
        #
        #  @return The keys in the LegacySessionFeatures dictionary.
        @property
        def FeatureNames(self):
            return self._features.keys()

        ## Function to initialize any previously uninitialized values of per-level features to 0, for given level.
        #  This means we can have "None" values for unreached levels, and 0's for features that
        #  simply never got incremented.
        #  @param level The level for which we should initialize values.
        def initLevel(self, level) -> None:
            for f_name in self._perlevel_names:
                feature = self._features[f_name]
                if type(feature) is dict and level in feature.keys():
                    if feature[level]["val"] == None:
                        feature[level]["val"] = 0
                else:
                    Logger.Log(f"Tried to initialize invalid level {level} for feature {f_name}", logging.ERROR)

        ## Function to get value of a per-count feature (including per-level)
        #  For a per-level feature, index is the level.
        #
        #  @param feature_name The name of the feature to retrieve
        #  @param index        The count index of the specific value, e.g. the level
        #  @return             The value stored for the given feature at given index.
        def getValByIndex(self, feature_name: str, index: int) -> Optional[Any]:
            if self._has_feature(feature_name):
                feature = self._features[feature_name]
                if type(feature) is dict and index in feature.keys():
                    return feature[index]["val"]
                else:
                    Logger.Log(f"Tried to get value on invalid index of {feature_name}: {index}", logging.ERROR)
            else:
                return None

        ## Function to get whole feature of a per-count feature (including per-level)
        #  For a per-level feature, index is the level.
        #
        #  @param feature_name The name of the feature to retrieve
        #  @param index        The count index of the desired value, e.g. the level
        #  @return             The feature stored for the given feature at given index.
        #                      This feature is a dictionary with a "val" and "prefix"
        def getFeatureByIndex(self, feature_name: str, index: int) -> Optional[Any]:
            if self._has_feature(feature_name):
                feature = self._features[feature_name]
                if type(feature) is dict and index in feature.keys():
                    return feature[index]
                else:
                    Logger.Log(f"Tried to get feature on invalid index of {feature_name}: {index}", logging.ERROR)
            else:
                return None

        ## Function to get all data on a given feature.
        #  Generally, this is intended for getting the value of an aggregate feature.
        #  However, it may also be used to get data across all levels/count for a
        #  per-count feature.
        #
        #  @param feature_name The name of the feature to retrieve
        #  @return             The value stored for the given feature.
        def getValByName(self, feature_name: str) -> Optional[Any]:
            if self._has_feature(feature_name):
                return self._features[feature_name]
            else:
                return None

        ## Function to set value of a per-count feature (including per-level)
        #  For a per-level feature, index is the level.
        #
        #  @param feature_name The name of the feature to set
        #  @param index        The count index of the desired value, e.g. the level
        #  @param new_value    The value to be stored for the given feature at given index.
        def setValByIndex(self, feature_name: str, index: int, new_value) -> None:
            if self._has_feature(feature_name):
                feature = self._features[feature_name]
                if type(feature) is dict and index in feature.keys():
                    feature[index]["val"] = new_value
                else:
                    Logger.Log(f"Tried to set value on invalid index of {feature_name}: {index}", logging.ERROR)

        ## Function to set value of a per-level feature
        #  Pure syntax sugar, calls setValByIndex using level as the index.
        #
        #  @param feature_name The name of the feature to set
        #  @param index        The count index of the desired value, e.g. the level
        #  @param new_value    The value to be stored for the given feature at given index.
        def setValByLevel(self, feature_name: str, level: int, new_value) -> None:
            self.setValByIndex(feature_name=feature_name, index=level, new_value=new_value)

        ## Function to set value of a full feature
        #  Intended for use with aggregate features. Not recommended for setting
        #  per-count features.
        #
        #  @param feature_name The name of the feature to retrieve
        #  @param new_value    The value to be stored for the given feature.
        def setValByName(self, feature_name: str, new_value) -> None:
            if self._has_feature(feature_name):
                self._features[feature_name] = new_value

        ## Function to increment the value of a per-count feature (including per-level)
        #  For a per-level feature, index is the level.
        #
        #  @param feature_name The name of the feature to increment
        #  @param index        The count index of the specific value, e.g. the level
        #  @param increment    The size of the increment (default = 1)
        def incValByIndex(self, feature_name: str, index: int, increment: Union[int, float] = 1) -> None:
            if self._has_feature(feature_name):
                feature = self._features[feature_name]
                if type(feature) is dict and index in feature.keys():
                    old_val = feature[index]["val"]
                    if old_val == 'null':
                        feature[index]["val"] = 0
                    elif (isinstance(old_val, int)) \
                      or (isinstance(old_val, float)):
                        feature[index]["val"] += increment
                    elif isinstance(old_val, timedelta):
                        feature[index]["val"] = old_val + timedelta(seconds=increment)
                else:
                    Logger.Log(f"Tried to increment value on invalid index of {feature_name}: {index}", logging.ERROR)

        ## Function to increment the value of a per-level feature
        #  Pure syntax sugar, calls incValByIndex using level as the index.
        #
        #  @param feature_name The name of the feature to increment
        #  @param index        The count index of the specific value, e.g. the level
        #  @param increment    The size of the increment (default = 1)
        def incValByLevel(self, feature_name: str, level: int, increment: Union[int, float] = 1) -> None:
            self.incValByIndex(feature_name=feature_name, index=level, increment=increment)

        ## Function to increment value of an aggregate feature
        #
        #  @param feature_name The name of the feature to increment
        #  @param increment    The size of the increment (default = 1)
        def incAggregateVal(self, feature_name: str, increment: Union[int, float] = 1) -> None:
            if self._has_feature(feature_name):
                old_val = self._features[feature_name]
                if (isinstance(old_val, int)) \
                or (isinstance(old_val, float)):
                    self._features[feature_name] = old_val + increment
                elif isinstance(old_val, timedelta):
                    self._features[feature_name] = old_val + timedelta(seconds=increment)
                else:
                    Logger.Log(f"In LegacyFeature, tried to increment {feature_name} of non-numeric type {type(self._features[feature_name])} by {increment} of type {type(increment)}", logging.WARN)
            else:
                Logger.Log("Attempted to increment a feature that doesn't exist!", logging.WARN)

        def _has_feature(self, feature_name) -> bool:
            try:
                _ = self._features[feature_name]
            except KeyError:
                Logger.Log(f'Feature {feature_name} does not exist.', logging.ERROR)
                return False
            return True
