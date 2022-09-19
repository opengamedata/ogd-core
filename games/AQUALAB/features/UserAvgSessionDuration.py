# import libraries
from typing import Any, List
# import locals
from extractors.Extractor import ExtractorParameters
from extractors.features.SessionFeature import SessionFeature
from schemas.Event import Event
from schemas.FeatureData import FeatureData

class UserAvgSessionDuration(SessionFeature):

    def __init__(self, params:ExtractorParameters, player_id:str):
        self._player_id = player_id
        super().__init__(params=params)
        self._times = []

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["SessionDuration"]

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature:FeatureData):
        if feature.PlayerID == self._player_id:
            if feature.FeatureValues[0] == "No events":
                pass
            else:
                self._times.append(feature.FeatureValues[0].seconds)

    def _getFeatureValues(self) -> List[Any]:
        if len(self._times) > 0:
            return [sum(self._times) / len(self._times)]
        else:
            return [0]

    # *** Optionally override public functions. ***
