## import standard libraries
import abc
import logging
from os import sep
import typing
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple, Union
## import local files
import utils
from extractors.Feature import Feature
from schemas.Event import Event
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

    # @abc.abstractmethod
    # def _extractFromEvent(self, event:Event):
    #     """Abstract declaration of a function to perform extraction of features from a row.

    #     :param event: [description]
    #     :type event: Event
    #     :param table_schema: A data structure containing information on how the db
    #                          table assiciated with this game is structured.
    #     :type table_schema: TableSchema
    #     """
    #     pass

    # *** PUBLIC BUILT-INS ***

    # Base constructor for LegacyFeature classes.
    def __init__(self, name:str, description:str, count_index:int, game_schema:GameSchema, session_id:str):
        """Base constructor for LegacyFeature classes.
        The constructor sets an extractor's session id and range of levels,
        as well as initializing the features dictionary and list of played levels.

        :param session_id: The id of the session from which we will extract features.
        :type session_id: int
        :param game_schema: A dictionary that defines how the game data itself is structured
        :type game_schema: GameSchema
        """
        super().__init__(name=name, description=description, count_index=count_index)
        self._session_id  : str         = session_id
        self._levels      : List[int]   = []
        self._sequences   : List        = []
        self._features    : LegacyFeature.LegacySessionFeatures = LegacyFeature.LegacySessionFeatures(game_schema=game_schema)

    # *** PUBLIC STATICS ***

    # Static function to print column headers to a file.
    # @staticmethod
    # def WriteFileHeader(game_schema: GameSchema, file: typing.IO[str], separator:str="\t") -> None:
    #     """Static function to print column headers to a file.
    #     We first create a feature dictionary, then essentially write out each key,
    #     with some formatting to add prefixes to features that repeat per-level
    #     (or repeat with a custom count).

    #     :param game_schema: A dictionary that defines how the game data itself is structured.
    #     :type game_schema: GameSchema
    #     :param file: An open csv file to which we will write column headers.
    #     :type file: typing.IO[str]
    #     :param separator: [description], defaults to "\t"
    #     :type separator: str, optional
    #     """
    #     columns = LegacyFeature.GetFeatureNames(game_schema=game_schema)
    #     file.write(separator.join(columns))
    #     file.write("\n")

    # *** PUBLIC METHODS ***

    def GetFeatureNames(self, game_schema:GameSchema) -> List[str]:
        columns = []
        features = LegacyFeature.LegacySessionFeatures.generateFeatureDict(game_schema)
        for feature_name,feature_content in features.items():
            if type(feature_content) is dict:
                # if it's a dictionary, expand.
                columns.extend([f"{feature_content[num]['prefix']}{num}_{feature_name}" for num in feature_content.keys()])
            else:
                columns.append(str(feature_name))
        return columns

    def GetFeatureValues(self) -> List[Any]:
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

    # def ExtractFromEvent(self, event:Event) -> None:
        # self._extractSequencesFromEvent(event=event, table_schema=table_schema)
        # self._extractFeaturesFromEvent(event=event)

    # def CalculateAggregateFeatures(self) -> None:
    #     """Overridden version of a blank function from Extractor, purely for compatibility with old extractors.
    #     Just call the abstract function that does actual work in all LegacyFeatures.
    #     """
    #     self._calculateAggregateFeatures()

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    # def _extractSequencesFromEvent(self, event:Event, table_schema:TableSchema) -> None:
    #     for sequence in self._sequences:
    #         event_data = self.extractCustomSequenceEventDataFromRow(event=event, table_schema=table_schema)
    #         sequence.RegisterEvent(event.event_data, event_data=event_data)

    ## Function to custom-extract event data for a sequence.
    #  *** This function MUST BE OVERRIDDEN if you want sequence data other than the event types. ***
    #  For now, it's assumed that all sequences an extractor might want to record have a common custom-data need.
    #  At the very least, the extractor could take the union of all data its various sequences may need.
    #  In general, however, if the extractor needs multiple kinds of sequences or sequence data,
    #  it is probably better to do dedicated sequence analysis.
    # def extractCustomSequenceEventDataFromRow(self, event:Event, table_schema:TableSchema):
    #     return None


    ## @class LegacySessionFeatures
    #  Private LegacyFeature class to track feature data.
    #  This class provides several functions to manage data, which should make
    #  the actual extractor code easier to read/write, since there is less need
    #  to understand the structure of feature data.
    class LegacySessionFeatures:
        def __init__(self, game_schema: GameSchema):
            self.perlevels: List[str] = list(game_schema.perlevel_features().keys())
            self.features = LegacyFeature.LegacySessionFeatures.generateFeatureDict(game_schema)

        @staticmethod
        def generateFeatureDict(game_schema: GameSchema) -> Dict[str,Union[int,float,Dict[int,Dict[str,Any]]]]:
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
            perlevels = game_schema.perlevel_features()
            level_range = range(game_schema._min_level   if game_schema._min_level is not None else 0,
                                game_schema._max_level+1 if game_schema._max_level is not None else 1)
            features : Dict[str,Union[int,float,Dict[int,Dict[str,Any]]]] = {f:{lvl:{"val":None, "prefix":"lvl"} for lvl in level_range } for f in perlevels.keys()}
            # next, do something similar for other per-custom-count features.
            percounts = game_schema.percount_features()
            features.update({f:{num:{"val":None, "prefix":percounts[f]["prefix"]} for num in range(0, percounts[f]["count"]) } for f in percounts})
            # finally, add in aggregate-only features.
            features.update({f:0 for f in game_schema.aggregate_features().keys()})
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
                    utils.Logger.Log(f"Tried to intialize invalid level: {level}", logging.ERROR)

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
                    utils.Logger.Log(f"Tried to get value on invalid index of {feature_name}: {index}", logging.ERROR)
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
                    utils.Logger.Log(f"Tried to get feature on invalid index of {feature_name}: {index}", logging.ERROR)
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
                    utils.Logger.Log(f"Tried to set value on invalid index of {feature_name}: {index}", logging.ERROR)

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
                    utils.Logger.Log(f"Tried to increment value on invalid index of {feature_name}: {index}", logging.ERROR)

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
                self.features[feature_name] += increment

        def _has_feature(self, feature_name) -> bool:
            try:
                _ = self.features[feature_name]
            except KeyError:
                utils.Logger.Log(f'Feature {feature_name} does not exist.', logging.ERROR)
                return False
            return True

    ## Simple helper class to track a sequence of events, based on move types.
    class Sequence:
        def __init__(self, end_function: typing.Callable[[List[Tuple]], None], end_event_type, end_event_count:int=1):
            self._fnEnd          = end_function
            self._end_event_type  = end_event_type
            self._end_event_count = 0               # current count of end events
            self._end_at_count    = end_event_count # number of end events to count before ending the sequence.
            self._events          = []

        def RegisterEvent(self, event_type, event_data) -> None:
            self._events.append((event_type, event_data))
            if event_type == self._end_event_type:
                self._end_event_count += 1
            if self._end_event_count == self._end_at_count:
                self._fnEnd(self._events)


