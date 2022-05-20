from collections import defaultdict
from typing import Any, List

from schemas.FeatureData import FeatureData
from features.SessionFeature import SessionFeature
from schemas.Event import Event

class PopulationSummary(SessionFeature):

    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description)
        self._user_sessions = defaultdict(list)
        self._user_completions = defaultdict(list)
        self._user_session_times = defaultdict(list)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return []

    def _getFeatureDependencies(self) -> List[str]:
        return ["JobsCompleted", "SessionID", "SessionDuration"]

    def _extractFromEvent(self, event: Event) -> None:
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        if feature.Name == "JobsCompleted":
            self._user_completions[feature.PlayerID].append(feature.FeatureValues[0])
        elif feature.Name == "SessionID" and feature.SessionID not in self._user_sessions[feature.PlayerID]:
            self._user_sessions[feature.PlayerID].append(feature.SessionID)
        elif feature.Name == "SessionDuration":
            self._user_session_times[feature.PlayerID].append(feature.FeatureValues[0])

    def _getFeatureValues(self) -> List[Any]:
        num_sessions = [len(self._user_sessions[user]) for user in self._user_sessions]
        num_completions = [len(self._user_completions[user]) for user in self._user_completions]
        session_times = []

        for user in self._user_session_times:
            for time in self._user_session_times[user]:
                session_times.append(time)

        summary = {
            "avg_session_count": 0,
            "avg_jobs_completed": 0,
            "avg_session_time": 0
        }

        if len(num_sessions) > 0:
            summary["avg_session_count"] = int(sum(num_sessions) / len(num_sessions))

        if len(num_completions) > 0:
            summary["avg_jobs_completed"] = int(sum(num_completions) / len(num_completions))

        if len(session_times) > 0:
            summary["avg_session_time"] = sum(session_times) / len(session_times)

        return [summary]

    # *** Optionally override public functions. ***
