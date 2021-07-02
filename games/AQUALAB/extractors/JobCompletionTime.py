from typing import Any, List

from extractors.Feature import Feature
from schemas.Event import Event

class JobCompletionTime(Feature):

    def __init__(self, name:str, description:str, sessionID:str):
        min_data_version = None
        max_data_version = None
        super().__init__(name, description, min_data_version, max_data_version)
        self._sessionID = sessionID
        self._job_start_time = None
        self._times = {}

    def GetEventTypes(self) -> List[str]:
        return []

    def CalculateFinalValues(self) -> Any:
        return self._times

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_name == "accept_job":
            self._job_start_time = event.timestamp
        elif event.event_name == "complete_job":
            self._times[event.event_data["job_id"]] = event.timestamp - self._job_start_time
            self._job_start_time = None
