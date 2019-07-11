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
        pass

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