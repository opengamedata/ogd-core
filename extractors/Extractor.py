## import standard libraries
import abc
import logging
import typing
import logging
from datetime import datetime
from typing import Any, Dict, List, Tuple, Union
## import local files
import utils
from schemas.Event import Event
from schemas.GameSchema import GameSchema
from schemas.TableSchema import TableSchema
from collections import defaultdict
from datetime import timedelta

## @class Extractor
#  Abstract base class for game feature extractors.
#  Gives a few static functions to be used across all extractor classes,
#  and defines an interface that the SessionProcessor can use.
class Extractor(abc.ABC):
    ## @var GameSchema _schema
    #  The schema specifying structure of data associated with an extractor.
    _schema: GameSchema

    ## Base constructor for Extractor classes.
    #  The constructor sets an extractor's session id and range of levels,
    #  as well as initializing the features dictionary and list of played levels.
    #
    #  @param session_id  The id of the session from which we will extract features.
    #  @param game_schema A dictionary that defines how the game data itself is
    #                     structured.
    def __init__(self, session_id: int, game_schema: GameSchema):
        self._session_id  : int         = session_id
        self._game_schema : GameSchema
        self._levels      : List[int]   = []
        self._sequences   : List        = []
        self._features    : Extractor.SessionFeatures = Extractor.SessionFeatures(game_schema=game_schema)
        self._last_adjust_type : Union[str,None] = None

    ## Static function to print column headers to a file.
    #  We first create a feature dictionary, then essentially write out each key,
    #  with some formatting to add prefixes to features that repeat per-level
    #  (or repeat with a custom count).
    #
    #  @param game_schema A dictionary that defines how the game data itself is
    #                     structured.
    #  @param file        An open csv file to which we will write column headers.
    @staticmethod
    def writeCSVHeader(game_schema: GameSchema, file: typing.IO[str]) -> None:
        columns = Extractor.getFeatureNames(game_schema=game_schema)
        file.write(",".join(columns))
        file.write("\n")

    @staticmethod
    def getFeatureNames(game_schema: GameSchema) -> List[str]:
        columns = []
        features = Extractor.SessionFeatures.generateFeatureDict(game_schema)
        for key in features.keys():
            if type(features[key]) is type({}):
                # if it's a dictionary, expand.
                columns.extend([f"{features[key][num]['prefix']}{num}_{key}" for num in features[key].keys()])
            else:
                columns.append(str(key))
        return columns

    ## Function to print data from an extractor to file.
    #  This function should be the same across all Extractor subtypes.
    #  Simply prints out each value from the extractor's features dictionary.
    #
    #  @param file        An open csv file to which we will write column headers.
    def writeCurrentFeatures(self, file: typing.IO[str]) -> None:
    # TODO: It looks like I might be assuming that dictionaries always have same order here.
    # May need to revisit that issue. I mean, it should be fine because Python won't just go
    # and change order for no reason, but still...
        column_vals = self.getCurrentFeatures()
        file.write(",".join(column_vals))
        file.write("\n")

    def getCurrentFeatures(self) -> typing.List[str]:
        def myformat(obj):
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
                column_vals.extend([myformat(self._features.getValByIndex(key, num)) for num in self._features.getValByName(feature_name=key).keys()])
            else:
                column_vals.append(myformat(self._features.getValByName(key)))
        return column_vals

    def extractFromRow(self, event:Event, table_schema:TableSchema) -> None:
        self.extractSequencesFromRow(event=event, table_schema=table_schema)
        self.extractFeaturesFromEvent(event=event, table_schema=table_schema)

    def extractSequencesFromRow(self, event:Event, table_schema:TableSchema) -> None:
        for sequence in self._sequences:
            event_data = self.extractCustomSequenceEventDataFromRow(event=event, table_schema=table_schema)
            sequence.RegisterEvent(event.event_data, event_data=event_data)

    ## Function to custom-extract event data for a sequence.
    #  *** This function MUST BE OVERRIDDEN if you want sequence data other than the event types. ***
    #  For now, it's assumed that all sequences an extractor might want to record have a common custom-data need.
    #  At the very least, the extractor could take the union of all data its various sequences may need.
    #  In general, however, if the extractor needs multiple kinds of sequences or sequence data,
    #  it is probably better to do dedicated sequence analysis.
    def extractCustomSequenceEventDataFromRow(self, event:Event, table_schema:TableSchema):
        return None

    ## Abstract declaration of a function to perform extraction of features from a row.
    #
    #  @param row_with_complex_parsed A row of game data from the db, with the
    #                                 "complex data" already parsed from JSON.
    #  @param table_schema  A data structure containing information on how the db
    #                     table assiciated with this game is structured.
    @abc.abstractmethod
    def extractFeaturesFromEvent(self, event:Event, table_schema:TableSchema):
        pass

    ## Abstract declaration of a function to perform calculation of aggregate features
    #  from existing per-level/per-custom-count features.
    @abc.abstractmethod
    def calculateAggregateFeatures(self):
        pass

    ## @class SessionFeatures
    #  Private Extractor class to track feature data.
    #  This class provides several functions to managing data, which should make
    #  the actual extractor code easier to read/write, since there is less need
    #  to understand the structure of feature data.
    class SessionFeatures:
        def __init__(self, game_schema: GameSchema):
            self.perlevels: List = list(game_schema.perlevel_features().keys())
            self.features = Extractor.SessionFeatures.generateFeatureDict(game_schema)

        ## Static function to generate a dictionary of game feature data from a given schema.
        #  The dictionary has the following hierarchy:
        #  feature_dict -> [individual features] -> [individual levels] -> {value, prefix}
        #
        #  @param level_range The range of all levels for the game associated with an extractor.
        #  @param game_schema A dictionary that defines how the game data is structured.
        @staticmethod
        def generateFeatureDict(game_schema: GameSchema) -> Dict[str,Union]:
            # construct features as a dictionary that maps each per-level feature to a sub-dictionary,
            # which in turn maps each level to a value and prefix.
            perlevels = game_schema.perlevel_features()
            level_range = range(game_schema.min_level   if game_schema.min_level is not None else 0,
                                game_schema.max_level+1 if game_schema.max_level is not None else 1)
            features : Dict[str,Union[int,float,Dict[int,Dict[str,Any]]]] = {f:{lvl:{"val":None, "prefix":"lvl"} for lvl in level_range } for f in perlevels.keys()}
            # next, do something similar for other per-custom-count features.
            percounts = game_schema.percount_features()
            features.update({f:{num:{"val":None, "prefix":percounts[f]["prefix"]} for num in range(0, percounts[f]["count"]) } for f in percounts})
            # finally, add in aggregate-only features.
            features.update({f:0 for f in game_schema.aggregate_features().keys()})
            return features

        ## Getter function to retrieve a list of all features in the SessionFeatures dictionary.
        #
        #  @return The keys in the SessionFeatures dictionary.
        def featureList(self):
            return self.features.keys()

        ## Function to initialize any previously uninitialized values of per-level features to 0, for given level.
        #  This means we can have "None" values for unreached levels, and 0's for features that
        #  simply never got incremented.
        #  @param level The level for which we should initialize values.
        def initLevel(self, level) -> None:
            for f_name in self.perlevels:
                if self.features[f_name][level]["val"] == None:
                    self.features[f_name][level]["val"] = 0

        ## Function to get value of a per-count feature (including per-level)
        #  For a per-level feature, index is the level.
        #
        #  @param feature_name The name of the feature to retrieve
        #  @param index        The count index of the specific value, e.g. the level
        #  @return             The value stored for the given feature at given index.
        def getValByIndex(self, feature_name: str, index: int) -> Any:
            if not self._verify_feature(feature_name):
                return None
            return self.features[feature_name][index]["val"]

        ## Function to get whole feature of a per-count feature (including per-level)
        #  For a per-level feature, index is the level.
        #
        #  @param feature_name The name of the feature to retrieve
        #  @param index        The count index of the desired value, e.g. the level
        #  @return             The feature stored for the given feature at given index.
        #                      This feature is a dictionary with a "val" and "prefix"
        def getFeatureByIndex(self, feature_name: str, index: int) -> Any:
            if not self._verify_feature(feature_name):
                return None
            return self.features[feature_name][index]

        ## Function to get all data on a given feature.
        #  Generally, this is intended for getting the value of an aggregate feature.
        #  However, it may also be used to get data across all levels/count for a
        #  per-count feature.
        #
        #  @param feature_name The name of the feature to retrieve
        #  @return             The value stored for the given feature.
        def getValByName(self, feature_name: str) -> Any:
            if not self._verify_feature(feature_name):
                return None
            return self.features[feature_name]

        ## Function to set value of a per-count feature (including per-level)
        #  For a per-level feature, index is the level.
        #
        #  @param feature_name The name of the feature to set
        #  @param index        The count index of the desired value, e.g. the level
        #  @param new_value    The value to be stored for the given feature at given index.
        def setValByIndex(self, feature_name: str, index: int, new_value) -> None:
            if not self._verify_feature(feature_name):
                return
            self.features[feature_name][index]["val"] = new_value

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
            if not self._verify_feature(feature_name):
                return
            self.features[feature_name] = new_value

        ## Function to increment the value of a per-count feature (including per-level)
        #  For a per-level feature, index is the level.
        #
        #  @param feature_name The name of the feature to increment
        #  @param index        The count index of the specific value, e.g. the level
        #  @param increment    The size of the increment (default = 1)
        def incValByIndex(self, feature_name: str, index: int, increment: Union[int, float] = 1) -> None:
            if not self._verify_feature(feature_name):
                return
            if self.features[feature_name][index]["val"] == 'null':
                self.features[feature_name][index]["val"] = 0
            self.features[feature_name][index]["val"] += increment

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
            if not self._verify_feature(feature_name):
                return
            self.features[feature_name] += increment

        def _verify_feature(self, feature_name) -> bool:
            try:
                _ = self.features[feature_name]
            except KeyError:
                utils.Logger.Log(f'{feature_name} does not exist.', logging.ERROR)
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


