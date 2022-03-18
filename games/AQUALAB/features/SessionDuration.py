import json
from datetime import datetime
from typing import Any, List

from features.SessionFeature import SessionFeature
from features.FeatureData import FeatureData
from schemas.Event import Event

class SessionDuration(SessionFeature):

    def __init__(self, name:str, description:str, session_id:str):
        self._session_id = session_id
        super().__init__(name=name, description=description)
        self._client_start_time = None
        self._session_duration = 0

    def GetEventDependencies(self) -> List[str]:
        return []

    def GetFeatureDependencies(self) -> List[str]:
        return ["EventList"]

    def GetFeatureValues(self) -> List[Any]:
        return [self._session_duration]

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        events = json.loads(feature.FeatureValues()[0])

        for event in events:
            if event["session_id"] == self._session_id:
                time = datetime.strptime(event["timestamp"], "%Y-%m-%dT%H:%M:%S")

                if not self._client_start_time:
                    self._client_start_time = time
                else:
                    self._session_duration = (time - self._client_start_time).total_seconds()
