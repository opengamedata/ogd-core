## import standard libraries
import abc
import math
import typing
from typing import List, Union
# Local imports
from schemas.Event import Event

## @class Model
#  Abstract base class for session-level Wave features.
#  Models only have one public function, called Eval.
#  The Eval function takes a list of row data, computes some statistic, and returns a list of results.
#  If the model works on features from session data, it should calculate one result for each row (each row being a session).
#  If the model works on a raw list of recent events, it should calculate a single result (each row being an event).
class Feature(abc.ABC):
    def __init__(self, min_data_version:Union[str,None]=None, max_data_version:Union[str,None]=None):
        self._min_data_version = min_data_version
        self._max_data_version = max_data_version

    ## Abstract function to get a list of event types the Feature wants.
    @abc.abstractmethod
    def GetEventTypes(self) -> List[str]:
        pass
    
    @abc.abstractmethod
    def CalculateFinalValues(self) -> typing.Tuple:
        pass

    def ExtractFromEvent(self, event:Event):
        event_type = event.event_name.split('.')[0]
        if self._validateVersion(event.app_version) and self._validateEventType(event_type if event_type != "CUSTOM" else event.event_data["event_custom"]):
            self._extractFromEvent(event)

    ## Abstract declaration of a function to perform update of a feature from a row.
    #
    #  @param row : A row, which will be used to update the feature's data.
    @abc.abstractmethod
    def _extractFromEvent(self, event:Event):
        pass

    ## Private function to check whether the given data version from a row is acceptable by this feature extractor.
    def _validateVersion(self, data_version:str) -> bool:
        if self._min_data_version is not None:
            if Event.CompareVersions(data_version, self._min_data_version) < 0:
                return False # too old, not valid.
        if self._max_data_version is not None:
            if Event.CompareVersions(data_version, self._max_data_version) > 0:
                return False # too new, not valid
        return True # passed both cases, valid.

    def _validateEventType(self, event_type:str) -> bool:
        if event_type in self.GetEventTypes():
            return True
        else:
            return False