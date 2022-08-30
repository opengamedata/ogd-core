## import standard libraries
import abc
import logging
import typing
import logging
from collections import defaultdict
from datetime import timedelta
from typing import Any, Dict, List, Optional, Union
## import local files
from utils import Logger
from extractors.Extractor import ExtractorParameters
from extractors.features.Feature import Feature
from schemas.FeatureData import FeatureData
from schemas.GameSchema import GameSchema

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

    # *** BUILT-INS ***

    # Base constructor for LegacyFeature classes.
    def __init__(self, params:ExtractorParameters, game_schema:GameSchema, session_id:str):
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
        super().__init__(params=params)
        self._levels      : List[int]   = []
        self._sequences   : List        = []
        self._features    : LegacyFeature.LegacySessionFeatures = LegacyFeature.LegacySessionFeatures(game_schema=game_schema)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _getEventDependencies(self) -> List[str]:
        return ["all_events"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromFeatureData(self, feature: FeatureData):
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
        for key in self._features.featureList():
            key_type = type(self._features.getValByName(key))
            if key_type is type({}) or key_type is type(defaultdict()):
                # if it's a dictionary, expand.
                column_vals.extend([_format(self._features.getValByIndex(key, num)) for num in self._features.getValByName(feature_name=key).keys()])
            else:
                column_vals.append(_format(self._features.getValByName(key)))
        return column_vals

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***


    def GetFeatureNames(self) -> List[str]:
        columns = []
        features = LegacyFeature.LegacySessionFeatures.generateFeatureDict(self._game_schema)
        for feature_name,feature_content in features.items():
            if type(feature_content) is dict:
                # if it's a dictionary, expand.
                columns.extend([f"{feature_content[num]['prefix']}{num}_{feature_name}" for num in feature_content.keys()])
            else:
                columns.append(str(feature_name))
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
            self.perlevels: List[str] = list(game_schema.Features['perlevel'].keys())
            self.features = LegacyFeature.LegacySessionFeatures.generateFeatureDict(game_schema)

        @staticmethod
        def generateFeatureDict(game_schema: GameSchema) -> Dict[str,Union[int,float,timedelta,Dict[int,Dict[str,Any]]]]:
            """Static function to generate a dictionary of game feature data from a given schema.
            The dictionary has the following hierarchy:
            feature_dict -> [individual features] -> [individual levels] -> {value, prefix}

            :param game_schema: A dictionary that defines how the game data is structured.
            :type game_schema: GameSchema
            :return: [description]
            :rtype: Dict[str,Union[int,float,Dict[int,Dict[str,Any]]]]
            """
            # construct features as a dictionary that maps each per-level feature to a sub-dictionary,
            # which in turn maps each level to a value and prefix.
            perlevels = game_schema.Features['perlevel']
            level_range = range(game_schema._min_level   if game_schema._min_level is not None else 0,
                                game_schema._max_level+1 if game_schema._max_level is not None else 1)
            features : Dict[str,Union[int,float,timedelta,Dict[int,Dict[str,Any]]]] = {f:{lvl:{"val":None, "prefix":"lvl"} for lvl in level_range } for f in perlevels.keys()}
            # next, do something similar for other per-custom-count features.
            percounts = game_schema.PerCountFeatures
            features.update({f:{num:{"val":None, "prefix":percounts[f]["prefix"]} for num in range(0, percounts[f]["count"]) } for f in percounts})
            # finally, add in aggregate-only features.
            features.update({f:0 for f in game_schema.AggregateFeatures.keys()})
            return features

        ## Getter function to retrieve a list of all features in the LegacySessionFeatures dictionary.
        #
        #  @return The keys in the LegacySessionFeatures dictionary.
        def featureList(self):
            return self.features.keys()

        ## Function to initialize any previously uninitialized values of per-level features to 0, for given level.
        #  This means we can have "None" values for unreached levels, and 0's for features that
        #  simply never got incremented.
        #  @param level The level for which we should initialize values.
        def initLevel(self, level) -> None:
            for f_name in self.perlevels:
                feature = self.features[f_name]
                if type(feature) is dict and level in feature.keys():
                    if feature[level]["val"] == None:
                        feature[level]["val"] = 0
                else:
                    Logger.Log(f"Tried to intialize invalid level: {level}", logging.ERROR)

        ## Function to get value of a per-count feature (including per-level)
        #  For a per-level feature, index is the level.
        #
        #  @param feature_name The name of the feature to retrieve
        #  @param index        The count index of the specific value, e.g. the level
        #  @return             The value stored for the given feature at given index.
        def getValByIndex(self, feature_name: str, index: int) -> Any:
            if self._has_feature(feature_name):
                feature = self.features[feature_name]
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
        def getFeatureByIndex(self, feature_name: str, index: int) -> Any:
            if self._has_feature(feature_name):
                feature = self.features[feature_name]
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
        def getValByName(self, feature_name: str) -> Any:
            if self._has_feature(feature_name):
                return self.features[feature_name]
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
                feature = self.features[feature_name]
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
                self.features[feature_name] = new_value

        ## Function to increment the value of a per-count feature (including per-level)
        #  For a per-level feature, index is the level.
        #
        #  @param feature_name The name of the feature to increment
        #  @param index        The count index of the specific value, e.g. the level
        #  @param increment    The size of the increment (default = 1)
        def incValByIndex(self, feature_name: str, index: int, increment: Union[int, float] = 1) -> None:
            if self._has_feature(feature_name):
                feature = self.features[feature_name]
                if type(feature) is dict and index in feature.keys():
                    if feature[index]["val"] == 'null':
                        feature[index]["val"] = 0
                    feature[index]["val"] += increment
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
                if (type(self.features[feature_name]) == int) \
                or (type(self.features[feature_name]) == float) \
                or (type(self.features[feature_name]) == timedelta):
                    self.features[feature_name] += increment
                else:
                    Logger.Log(f"In LegacyFeature, tried to increment {feature_name} of non-numeric type {type(self.features[feature_name])} by {increment} of type {type(increment)}", logging.WARN)
            else:
                Logger.Log("Attempted to increment a feature that doesn't exist!", logging.WARN)

        def _has_feature(self, feature_name) -> bool:
            try:
                _ = self.features[feature_name]
            except KeyError:
                Logger.Log(f'Feature {feature_name} does not exist.', logging.ERROR)
                return False
            return True
