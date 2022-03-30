# global imports
import json
from datetime import datetime
from typing import Any, List
# local imports
from features.SessionFeature import SessionFeature
from features.FeatureData import FeatureData
from schemas.Event import Event

class SessionDuration(SessionFeature):

    def __init__(self, name:str, description:str, session_id:str):
        self._session_id = session_id
        super().__init__(name=name, description=description)
        self._client_start_time = None
        self._session_duration = 0

    # *** Implement abstract functions ***
    def _getEventDependencies(self) -> List[str]:
        return ["all_events"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if not self._client_start_time:
            self._client_start_time = event.timestamp
        else:
            self._session_duration = (event.timestamp - self._client_start_time).total_seconds()

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._session_duration]

    # *** Optionally override public functions. ***
