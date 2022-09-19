# import libraries
from schemas import Event
from typing import Any, List, Optional
# import locals
from schemas.FeatureData import FeatureData
from extractors.features.SessionFeature import SessionFeature
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event

class SessionID(SessionFeature):
    def __init__(self, params:ExtractorParameters, sessionID:str):
        SessionFeature.__init__(self, params=params)
        self._sessionID = sessionID

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._sessionID]

    # *** Optionally override public functions. ***

