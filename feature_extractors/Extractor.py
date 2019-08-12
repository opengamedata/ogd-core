## import standard libraries
import abc
import typing
from datetime import datetime
## import local files
from GameTable import GameTable
from schemas.Schema import Schema

## @class Extractor
#  Abstract base class for game feature extractors.
#  Gives a few static functions to be used across all extractor classes,
#  and defines an interface that the ProcManager can use.
class Extractor(abc.ABC):
    ## @var Schema _schema
    #  The schema specifying structure of data associated with an extractor.
    _schema: Schema

    ## Base constructor for Extractor classes.
    #  The constructor sets an extractor's session id and range of levels,
    #  as well as initializing the features dictionary and list of played levels.
    #
    #  @param session_id  The id of the session from which we will extract features.
    #  @param game_table  A data structure containing information on how the db
    #                     table assiciated with this game is structured.
    #  @param game_schema A dictionary that defines how the game data itself is
    #                     structured.
    def __init__(self, session_id: int, game_table: GameTable, game_schema: Schema):
        self.session_id:   int               = session_id
        self.levels:       typing.List[int]  = []
        self._level_range: range             = range(game_table.min_level, game_table.max_level+1)
        self.last_adjust_type: str           = None
        self.features:     Extractor.SessionFeatures = Extractor.SessionFeatures(self._level_range, game_schema)

    ## Static function to print column headers to a file.
    #  We first create a feature dictionary, then essentially write out each key,
    #  with some formatting to add prefixes to features that repeat per-level
    #  (or repeat with a custom count).
    #
    #  @param game_table  A data structure containing information on how the db
    #                     table assiciated with this game is structured.
    #  @param game_schema A dictionary that defines how the game data itself is
    #                     structured.
    #  @param file        An open csv file to which we will write column headers.
    @staticmethod
    def writeCSVHeader(game_table: GameTable, game_schema: Schema, file: typing.IO.writable):
        columns = []
        features = Extractor.SessionFeatures.generateFeatureDict(range(game_table.min_level, game_table.max_level+1), game_schema)
        for key in features.keys():
            if type(features[key]) is type({}):
                # if it's a dictionary, expand.
                columns.extend(["{}{}_{}".format(features[key][num]["prefix"], num, key) for num in features[key].keys()])
            else:
                columns.append(key)
        file.write(",".join(columns))
        file.write("\n")

    ## Function to print data from an extractor to file.
    #  This function should be the same across all Extractor subtypes.
    #  Simply prints out each value from the extractor's features dictionary.
    #
    #  @param file        An open csv file to which we will write column headers.
    def writeCurrentFeatures(self, file: typing.IO.writable):
    # TODO: It looks like I might be assuming that dictionaries always have same order here.
    # May need to revisit that issue. I mean, it should be fine because Python won't just go
    # and change order for no reason, but still...
        column_vals = self.getCurrentFeatures()
        file.write(",".join(column_vals))
        file.write("\n")

    def getCurrentFeatures(self):
        column_vals = []
        for key in self.features.featureList():
            if type(self.features.getValByName(key)) is type({}):
                # if it's a dictionary, expand.
                column_vals.extend([str(self.features.getValByIndex(key, num)) for num in self.features.getValByName(feature_name=key).keys()])
            else:
                column_vals.append(str(self.features.getValByName(key)))
        return column_vals

    ## Abstract declaration of a function to perform extraction of features from a row.
    #
    #  @param row_with_complex_parsed A row of game data from the db, with the
    #                                 "complex data" already parsed from JSON.
    #  @param game_table  A data structure containing information on how the db
    #                     table assiciated with this game is structured.
    @abc.abstractmethod
    def extractFromRow(self, row_with_complex_parsed, game_table: GameTable):
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
        def __init__(self, level_range: range, game_schema: Schema):
            self.features = Extractor.SessionFeatures.generateFeatureDict(level_range, game_schema)

        ## Static function to generate a dictionary of game feature data from a given schema.
        #  The dictionary has the following hierarchy:
        #  feature_dict -> [individual features] -> [individual levels] -> {value, prefix}
        #
        #  @param level_range The range of all levels for the game associated with an extractor.
        #  @param game_schema A dictionary that defines how the game data is structured.
        @staticmethod
        def generateFeatureDict(level_range: range, game_schema: Schema):
            # construct features as a dictionary that maps each per-level feature to a sub-dictionary,
            # which in turn maps each level to a value and prefix.
            perlevels = game_schema.perlevel_features()
            features = {f:{lvl:{"val":0, "prefix":"lvl"} for lvl in level_range } for f in perlevels}
            # next, do something similar for other per-custom-count features.
            percounts = game_schema.percount_features()
            features.update({f:{num:{"val":0, "prefix":percounts[f]["prefix"]} for num in range(0, percounts[f]["count"]) } for f in percounts})
            # finally, add in aggregate-only features.
            features.update({f:0 for f in game_schema.aggregate_features()})
            return features

        ## Getter function to retrieve a list of all features in the SessionFeatures dictionary.
        #
        #  @return The keys in the SessionFeatures dictionary.
        def featureList(self):
            return self.features.keys()

        ## Function to get value of a per-count feature (including per-level)
        #  For a per-level feature, index is the level.
        #
        #  @param feature_name The name of the feature to retrieve
        #  @param index        The count index of the specific value, e.g. the level
        #  @return             The value stored for the given feature at given index.
        def getValByIndex(self, feature_name: str, index: int):
            return self.features[feature_name][index]["val"]

        ## Function to get whole feature of a per-count feature (including per-level)
        #  For a per-level feature, index is the level.
        #
        #  @param feature_name The name of the feature to retrieve
        #  @param index        The count index of the desired value, e.g. the level
        #  @return             The feature stored for the given feature at given index.
        #                      This feature is a dictionary with a "val" and "prefix"
        def getFeatureByIndex(self, feature_name: str, index: int):
            return self.features[feature_name][index]

        ## Function to get all data on a given feature.
        #  Generally, this is intended for getting the value of an aggregate feature.
        #  However, it may also be used to get data across all levels/count for a
        #  per-count feature.
        #
        #  @param feature_name The name of the feature to retrieve
        #  @return             The value stored for the given feature.
        def getValByName(self, feature_name: str):
            return self.features[feature_name]

        ## Function to set value of a per-count feature (including per-level)
        #  For a per-level feature, index is the level.
        #
        #  @param feature_name The name of the feature to set
        #  @param index        The count index of the desired value, e.g. the level
        #  @param new_value    The value to be stored for the given feature at given index.
        def setValByIndex(self, feature_name: str, index: int, new_value):
            self.features[feature_name][index]["val"] = new_value

        ## Function to set value of a full feature
        #  Intended for use with aggregate features. Not recommended for setting
        #  per-count features.
        #
        #  @param feature_name The name of the feature to retrieve
        #  @param new_value    The value to be stored for the given feature.
        def setValByName(self, feature_name: str, new_value):
            self.features[feature_name] = new_value

        ## Function to increment the value of a per-count feature (including per-level)
        #  For a per-level feature, index is the level.
        #
        #  @param feature_name The name of the feature to increment
        #  @param index        The count index of the specific value, e.g. the level
        #  @param increment    The size of the increment (default = 1)
        def incValByIndex(self, feature_name: str, index: int, increment: typing.Union[int, float] = 1):
            self.features[feature_name][index]["val"] += increment

        ## Function to increment value of an aggregate feature
        #
        #  @param feature_name The name of the feature to increment
        #  @param increment    The size of the increment (default = 1)
        def incAggregateVal(self, feature_name: str, increment: typing.Union[int, float] = 1):
            self.features[feature_name] += increment
