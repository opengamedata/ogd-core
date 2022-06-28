from typing import Any, List

from schemas.FeatureData import FeatureData
from extractors.features.SessionFeature import SessionFeature
from schemas.Event import Event

class PlayerSummary(SessionFeature):

    def __init__(self, params:ExtractorParameters):
        super().__init__(name=name, description=description)
        self._summary = {}

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return []

    def _getFeatureDependencies(self) -> List[str]:
        return ["JobsCompleted", "SessionDuration", "SessionID"]

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        user_id = feature.PlayerID

        if user_id not in self._summary:
            self._summary[user_id] = {
                "active_time": 0,
                "jobs_completed": [],
                "num_sessions": 0
            }

        if feature.Name == "JobsCompleted":
            self._summary[user_id]["jobs_completed"] = feature.FeatureValues[0]
        elif feature.Name == "SessionDuration":
            self._summary[user_id]["active_time"] += feature.FeatureValues[0]
        elif feature.Name == "SessionID":
            self._summary[user_id]["num_sessions"] += 1

    def _getFeatureValues(self) -> List[Any]:
        return [self._summary]

    # *** Optionally override public functions. ***
