from typing import Any, List

from schemas.FeatureData import FeatureData
from features.SessionFeature import SessionFeature
from schemas.Event import Event

class JobsCompleted(SessionFeature):

    def __init__(self, name:str, description:str, player_id:str):
        self._player_id = player_id
        super().__init__(name=name, description=description)
        self._jobs_completed = []

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["complete_job"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event: Event) -> None:
        if event.UserID == self._player_id:
            self._jobs_completed.append(event.EventData["job_name"]["string_value"])

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._jobs_completed]

    # *** Optionally override public functions. ***
