# import libraries
from typing import Any, List
# import locals
from extractors.features.SessionFeature import SessionFeature
from schemas.FeatureData import FeatureData
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event

class SessionDuration(SessionFeature):

    def __init__(self, params:ExtractorParameters, session_id:str):
        self._session_id = session_id
        super().__init__(params=params)
        self._client_start_time = None
        self._session_duration = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["all_events"]

    @classmethod
def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if not self._client_start_time:
            self._client_start_time = event.Timestamp
        else:
            self._session_duration = (event.Timestamp - self._client_start_time).total_seconds()

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._session_duration]

    # *** Optionally override public functions. ***
