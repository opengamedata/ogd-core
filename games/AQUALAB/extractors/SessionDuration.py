from datetime import timedelta
from typing import Any, List

from extractors.Feature import Feature
from schemas.Event import Event

class SessionDuration(Feature):

    def __init__(self, name:str, description:str, sessionID:str):
        min_data_version = None
        max_data_version = None
        super().__init__(name, description, min_data_version, max_data_version)
        self._sessionID = sessionID
        self._client_start_time = None
        self._session_duration = timedelta(0)

    def GetEventTypes(self) -> List[str]:
        return []

    def CalculateFinalValues(self) -> Any:
        return self._session_duration

    def _extractFromEvent(self, event:Event) -> None:
        if not self._client_start_time:
            self._client_start_time = event.timestamp

        self._session_duration = event.timestamp - self._client_start_time
