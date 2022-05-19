from typing import Any, List

from schemas.FeatureData import FeatureData
from features.SessionFeature import SessionFeature
from schemas.Event import Event

class PlayerSummary(SessionFeature):

    def __init__(self, name:str, description:str, player_id:str):
        self._player_id = player_id
        super().__init__(name=name, description=description)
        self._active_time = 0
        self._jobs_completed = []
        self._num_sessions = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["complete_job"]

    def _getFeatureDependencies(self) -> List[str]:
        return ["JobsAttempted", "SessionDuration", "SessionID"]

    def _extractFromEvent(self, event:Event) -> None:
        if event.user_id == self._player_id:
            job_name = event.event_data["job_name"]["string_value"]

            if job_name not in self._jobs_completed:
                self._jobs_completed.append(job_name)

    def _extractFromFeatureData(self, feature: FeatureData):
        if feature.Name == "SessionDuration" and feature.PlayerID == self._player_id:
            self._active_time += feature.FeatureValues[0]
        elif feature.Name == "SessionID" and feature.PlayerID == self._player_id:
            self._num_sessions += 1

    def _getFeatureValues(self) -> List[Any]:
        summary = {
            "active_time": self._active_time,
            "jobs_completed": self._jobs_completed,
            "num_sessions": self._num_sessions,
            "user_id": self._player_id
        }

        return [summary]

    # *** Optionally override public functions. ***
