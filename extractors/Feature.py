## import standard libraries
import abc
import math
import typing
from GameTable import GameTable

## @class Model
#  Abstract base class for session-level Wave features.
#  Models only have one public function, called Eval.
#  The Eval function takes a list of row data, computes some statistic, and returns a list of results.
#  If the model works on features from session data, it should calculate one result for each row (each row being a session).
#  If the model works on a raw list of recent events, it should calculate a single result (each row being an event).
class Feature(abc.ABC):
    def __init__(self, game_table: GameTable, min_data_version:int=-math.inf, max_data_version:int=math.inf):
        self._game_table = GameTable
        self._min_data_version = min_data_version
        self._max_data_version = max_data_version

    ## Abstract function to get a list of 
    @abc.abstractmethod
    def GetEventTypes(self):
        pass
    
    @abc.abstractmethod
    def CalculateFinalValues(self) -> typing.Tuple:
        pass

    def ExtractFromRow(self, row:typing.List):
        if self._validateVersion(row[self._game_table.app_version_index]) and self._validateEventType(row[self._game_table.complex_data_index["event_custom"]]):
            self._extractFromRow(row)

    ## Abstract declaration of a function to perform update of a feature from a row.
    #
    #  @param row : A row, which will be used to update the feature's data.
    @abc.abstractmethod
    def _extractFromRow(self, row: typing.List):
        pass

    ## Private function to check whether the given data version from a row is acceptable by this feature extractor.
    def _validateVersion(self, data_version:int) -> bool:
        if data_version < self._min_data_version or data_version > self._max_data_version:
            return False
        else:
            return True

    def _validateEventType(self, event_type:str) -> bool:
        if event_type in self.GetEventTypes():
            return True
        else:
            return False