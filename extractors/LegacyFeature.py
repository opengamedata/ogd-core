## import standard libraries
import abc
import typing
from typing import Any, Dict, List, Union
# Local imports
from extractors.Feature import Feature
from schemas.Event import Event

## @class Model
#  Abstract base class for session-level Wave features.
#  Models only have one public function, called Eval.
#  The Eval function takes a list of row data, computes some statistic, and returns a list of results.
#  If the model works on features from session data, it should calculate one result for each row (each row being a session).
#  If the model works on a raw list of recent events, it should calculate a single result (each row being an event).
class LegacyFeature(Feature):
    def __init__(self):
        super().__init__(name="LegacyFeature", description="Dummy LegacyFeature so old extractors don't break the system.")

    def __str__(self):
        return f"{self._name} : {self._desc}"

    ## Abstract function to get a list of event types the Feature wants.
    def GetEventTypes(self) -> List[str]:
        return []
    
    def CalculateFinalValues(self) -> typing.Tuple:
        return ()

    def ExtractFromEvent(self, event:Event):
        return

    ## Abstract declaration of a function to perform update of a feature from a row.
    #
    #  @param row : A row, which will be used to update the feature's data.
    def _extractFromEvent(self, event:Event):
        return

    ## Private function to check whether the given data version from a row is acceptable by this feature extractor.
    def _validateVersion(self, data_version:str) -> bool:
        return False

    def _validateEventType(self, event_type:str) -> bool:
        return False