# import libraries
from typing import Any, List
# import locals
from extractors.Extractor import ExtractorParameters
from extractors.features.SessionFeature import SessionFeature
from schemas.Event import Event
from schemas.FeatureData import FeatureData

class EchoSessionID(SessionFeature):

    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._session_id = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["SessionID"]

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature:FeatureData):
        self._session_id = feature.FeatureValues[0]

    def _getFeatureValues(self) -> List[Any]:
        return [f"The sess ID is: {self._session_id}"]

    # *** Optionally override public functions. ***
