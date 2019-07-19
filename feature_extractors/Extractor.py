## import standard libraries
import abc
import typing
from datetime import datetime
## import local files
from GameTable import GameTable
from schemas.Schema import Schema

# Abstract base class for game feature extractors.
class Extractor(abc.ABC):
    _schema: Schema

    def __init__(self, session_id: int, game_table: GameTable, game_schema: Schema):
        self.session_id:  int               = session_id
        self.last_adjust_type: str          = None
        self._level_range: range            = range(game_table.min_level, game_table.max_level+1)
        self.levels:      typing.List[int]  = []
        self.features:    typing.Dict       = Extractor._generateFeatureDict(self._level_range, game_schema)

    @staticmethod
    def _generateFeatureDict(level_range: range, game_schema: Schema):
        # construct features as a dictionary that maps each per-level feature to a sub-dictionary,
        # which maps each level to a value and prefix.
        perlevels = game_schema.perlevel_features()
        features = {f:{lvl:{"val":0, "prefix":"lvl"} for lvl in level_range } for f in perlevels}
        # next, do something similar for other per-custom-count features.
        percounts = game_schema.percount_features()
        features.update({f:{num:{"val":0, "prefix":percounts[f]["prefix"]} for num in range(0, percounts[f]["count"]) } for f in percounts})
        # finally, add in aggregate-only features.
        features.update({f:0 for f in game_schema.aggregate_features()})
        return features

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

    # TODO: It looks like I might be assuming that dictionaries always have same order here.
    # May need to revisit that issue. I mean, it should be fine because Python won't just go
    # and change order for no reason, but still...
    def writeCurrentFeatures(self, file: typing.IO.writable):
        column_vals = []
        for key in self.features.keys():
            if type(self.features[key]) is type({}):
                # if it's a dictionary, expand.
                column_vals.extend([str(self.features[key][num]["val"]) for num in self.features[key].keys()])
            else:
                column_vals.append(str(self.features[key]))
        file.write(",".join(column_vals))
        file.write("\n")

    @abc.abstractmethod
    def extractFromRow(self, row_with_complex_parsed, game_table: GameTable):
        pass

    @abc.abstractmethod
    def calculateAggregateFeatures(self):
        pass