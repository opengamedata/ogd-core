from collections import defaultdict
from typing import Any, List

from schemas.FeatureData import FeatureData
from features.SessionFeature import SessionFeature
from schemas.Event import Event

class PopulationSummary(SessionFeature):

    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description)
        self._session_completions = defaultdict(list)
        self._session_times = []

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return []

    def _getFeatureDependencies(self) -> List[str]:
        return ["JobsCompleted", "SessionDuration"]

    def _extractFromEvent(self, event: Event) -> None:
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        if feature.Name == "JobsCompleted":
            self._session_completions[feature.SessionID] = feature.FeatureValues[0]
        elif feature.Name == "SessionDuration":
            self._session_times.append(feature.FeatureValues[0])

    def _getFeatureValues(self) -> List[Any]:
        num_completions = [len(self._session_completions[session]) for session in self._session_completions]

        summary = {
            "avg_session_count": 1,
            "avg_jobs_completed": 0,
            "avg_session_time": 0
        }

        if len(num_completions) > 0:
            summary["avg_jobs_completed"] = sum(num_completions) / len(num_completions)

        if len(self._session_times) > 0:
            summary["avg_session_time"] = sum(self._session_times) / len(self._session_times)

        return [summary]

    # *** Optionally override public functions. ***
