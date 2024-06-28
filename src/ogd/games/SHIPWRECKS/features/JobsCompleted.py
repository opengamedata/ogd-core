from typing import Any, List

from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class JobsCompleted(SessionFeature):

    def __init__(self, params:GeneratorParameters, session_id:str):
        self._session_id = session_id
        super().__init__(params=params)
        self._jobs_completed = []

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["checkpoint"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        if event.EventData["status"] == "Case Closed" and event.SessionID == self._session_id:
            self._jobs_completed.append(event.EventData["mission_id"])

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._jobs_completed]

    # *** Optionally override public functions. ***
