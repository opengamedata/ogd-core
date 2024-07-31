from typing import Any, List

from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class PlayerSummary(SessionFeature):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._summary = {}

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["JobsCompleted", "SessionDuration"]

    def _updateFromEvent(self, event:Event) -> None:
        return

    def _updateFromFeatureData(self, feature:FeatureData):
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
