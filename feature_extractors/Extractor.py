## import standard libraries
import abc
import typing
from datetime import datetime
## import local files
from schemas.Schema import Schema

# Abstract base class for game feature extractors.
class Extractor(abc.ABC):
    _schema: Schema

    def __init__(self, session_id: int, max_level:int, min_level:int):
        self._session_id = session_id
        self._max_level  = max_level
        self._min_level  = min_level

    @abc.abstractmethod
    def extractFromRow(self, level:int, event_data_complex_parsed, event_client_time: datetime):
        pass

    @abc.abstractmethod
    def calculateAggregateFeatures(self):
        pass

    @abc.abstractmethod
    def writeCSVHeader(self, file: typing.IO.writable):
        pass

    @abc.abstractmethod
    def writeCurrentFeatures(self, file: typing.IO.writable):
        pass