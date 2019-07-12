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
        self.start_times: typing.Dict       = {}
        self.end_times:   typing.Dict       = {}
        self.features:    typing.Dict       = Extractor._generateFeatureDict(self._level_range, game_schema)

    @staticmethod
    def _generateFeatureDict(level_range: range, game_schema: Schema):
        # start with per-level features.
        # construct features as a dictionary that maps each per-level feature to a sub-dictionary,
        # which maps each level to a value.
        features = { f:{lvl:0 for lvl in level_range} for f in game_schema.perlevel_features() }
        # now, add custom-count features.
        features.update( {f:{num:0 for num in range(0, game_schema.percount_features()[f]["count"]) } for f in game_schema.percount_features()} )
        # finally, add in aggregate-only features.
        features.update({f:0 for f in game_schema.aggregate_features()})
        return features

    @abc.abstractmethod
    def extractFromRow(self, level:int, event_data_complex_parsed, event_client_time: datetime):
        pass

    @abc.abstractmethod
    def calculateAggregateFeatures(self):
        pass

    @staticmethod
    @abc.abstractmethod
    def writeCSVHeader(game_table: GameTable, game_schema: Schema, file: typing.IO.writable):
        pass

    @abc.abstractmethod
    def writeCurrentFeatures(self, file: typing.IO.writable):
        pass