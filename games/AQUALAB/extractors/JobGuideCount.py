from typing import Any, List

from extractors.Feature import Feature
from schemas.Event import Event

class JobGuideCount(Feature):

    def __init__(self, name:str, description:str, sessionID:str):
        min_data_version = None
        max_data_version = None
        super().__init__(name, description, min_data_version, max_data_version)
        self._sessionID = sessionID
        self._counts = {}

    def GetEventTypes(self) -> List[str]:
        return []

    def CalculateFinalValues(self) -> Any:
        return self._counts

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_data["job_id"] not in self._counts.keys:
            self._counts[event.event_data["job_id"]] = 0

        self._counts[event.event_data["job_id"]] += 1
