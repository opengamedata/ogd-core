from typing import Any, List

from extractors.Feature import Feature
from schemas.Event import Event

class SyncCompletionTime(Feature):

    def __init__(self, name:str, description:str):
        min_data_version = None
        max_data_version = None
        super().__init__(name=name, description=description, count_index=0, min_version=min_data_version, max_version=max_data_version)
        self._sim_start_time = None
        self._time = None

    def GetEventTypes(self) -> List[str]:
        return []

    def CalculateFinalValues(self) -> Any:
        return self._time

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_name == "begin_simulation":
            self._sim_start_time = event.timestamp
        elif event.event_name == "simulation_sync_achieved":
            self._time = event.timestamp - self._sim_start_time
