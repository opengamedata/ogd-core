from typing import Any, List

from schemas.FeatureData import FeatureData
from features.SessionFeature import SessionFeature
from schemas.Event import Event

class PlayerSummary(SessionFeature):

    def __init__(self, name:str, description:str, player_id:str):
        self._player_id = player_id
        super().__init__(name=name, description=description)
        self._summary = {}
        self._active_time = 0
        self._jobs_completed = []
        self._num_sessions = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["complete_job"]

    def _getFeatureDependencies(self) -> List[str]:
        return ["JobsAttempted", "SessionDuration", "SessionID"]

    def _extractFromEvent(self, event:Event) -> None:
        user_id = event.user_id
        job_name = event.event_data["job_name"]["string_value"]

        if user_id not in self._summary:
            self._summary[user_id] = {
                "active_time": 0,
                "jobs_completed": [],
                "num_sessions": 0
            }

        if job_name not in self._summary[user_id]["jobs_completed"]:
            self._summary[user_id]["jobs_completed"].append(job_name)

    def _extractFromFeatureData(self, feature: FeatureData):
        user_id = feature.PlayerID

        if user_id not in self._summary:
            self._summary[user_id] = {
                "active_time": 0,
                "jobs_completed": [],
                "num_sessions": 0
            }

        if feature.Name == "SessionDuration":
            self._summary[user_id]["active_time"] += feature.FeatureValues[0]
        elif feature.Name == "SessionID":
            self._summary[user_id]["num_sessions"] += 1

    def _getFeatureValues(self) -> List[Any]:
        return [self._summary]

    # *** Optionally override public functions. ***
