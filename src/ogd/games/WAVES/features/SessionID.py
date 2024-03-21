# import libraries
from ogd.core.schemas import Event
from typing import Any, List, Optional
# import locals
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.generators.Extractor import ExtractorParameters
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData

class SessionID(SessionFeature):
    def __init__(self, params:ExtractorParameters, sessionID:str):
        SessionFeature.__init__(self, params=params)
        self._sessionID = sessionID

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._sessionID]

    # *** Optionally override public functions. ***

