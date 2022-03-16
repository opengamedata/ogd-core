from typing import Any, List

from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class SessionDuration(Feature):

    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0)
        self._client_start_time = None
        self._session_duration = 0

    def GetEventDependencies(self) -> List[str]:
        return ["all_events"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        return [self._session_duration]

    def _extractFromEvent(self, event:Event) -> None:
        if not self._client_start_time:
            self._client_start_time = event.timestamp

        self._session_duration = (event.timestamp - self._client_start_time).total_seconds()

    def _extractFromFeatureData(self, feature: FeatureData):
        return
