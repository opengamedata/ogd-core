from typing import Any, List

from extractors.features.SessionFeature import SessionFeature
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData

class PlayerSummary(SessionFeature):

    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._summary = {}

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["JobsCompleted", "SessionDuration"]

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature:FeatureData):
        session_id = feature.SessionID

        if session_id not in self._summary:
            self._summary[session_id] = {
                "active_time": 0,
                "jobs_completed": [],
                "num_sessions": 1
            }

        if feature.FeatureType == "JobsCompleted":
            self._summary[session_id]["jobs_completed"] = feature.FeatureValues[0]
        elif feature.FeatureType == "SessionDuration":
            self._summary[session_id]["active_time"] += feature.FeatureValues[0]

    def _getFeatureValues(self) -> List[Any]:
        return [self._summary]

    # *** Optionally override public functions. ***
