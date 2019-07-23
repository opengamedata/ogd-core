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
        self.session_id:  int               = session_id
        self.last_adjust_type: str          = None
        self._level_range: range            = range(game_table.min_level, game_table.max_level+1)
        self.levels:      typing.List[int]  = []
        self.features:    typing.Dict       = Extractor._generateFeatureDict(self._level_range, game_schema)

    ## Static function to generate a dictionary of game feature data from a given schema.
    #  The dictionary has the following hierarchy:
    #  feature_dict -> [individual features] -> [individual levels] -> {value, prefix}
    #
    #  @param level_range The range of all levels for the game associated with an extractor.
    #  @param game_schema A dictionary that defines how the game data is structured.
    @staticmethod
    def _generateFeatureDict(level_range: range, game_schema: Schema):
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
        features = Extractor._generateFeatureDict(range(game_table.min_level, game_table.max_level+1), game_schema)
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
        column_vals = []
        for key in self.features.keys():
            if type(self.features[key]) is type({}):
                # if it's a dictionary, expand.
                column_vals.extend([str(self.features[key][num]["val"]) for num in self.features[key].keys()])
            else:
                column_vals.append(str(self.features[key]))
        file.write(",".join(column_vals))
        file.write("\n")

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