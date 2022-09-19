# import libraries
from typing import Any, List
# import locals
from extractors.Extractor import ExtractorParameters
from extractors.features.SessionFeature import SessionFeature
from schemas.Event import Event
from schemas.FeatureData import FeatureData

class UserSessionCount(SessionFeature):

    def __init__(self, params:ExtractorParameters, player_id:str):
        self._player_id = player_id
        super().__init__(params=params)
        self._count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
def _getEventDependencies(cls, mode:ExportMode) -> List[str]:
        return []

    @classmethod
def _getEventDependencies(cls, mode:ExportMode) -> List[str]:
        return ["SessionID"]

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature:FeatureData):
        if feature.PlayerID == self._player_id:
            self._count += 1

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***
