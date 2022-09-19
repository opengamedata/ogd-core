# import libraries
from schemas import Event
from typing import Any, List, Optional
# import locals
from schemas.FeatureData import FeatureData
from extractors.features.SessionFeature import SessionFeature
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event

class PersistentSessionID(SessionFeature):
    def __init__(self, params:ExtractorParameters):
        SessionFeature.__init__(self, params=params)
        self._persistent_id : Optional[int] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["BEGIN.0"]

    @classmethod
def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if self._persistent_id is None:
            self._persistent_id = event.EventData['persistent_session_id']

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._persistent_id]

    # *** Optionally override public functions. ***


