from typing import Any, List

from extractors.Feature import Feature
from schemas.Event import Event

class SyncCompletionTime(Feature):

    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0)
        self._sim_start_time = None
        self._time = None

    def GetEventTypes(self) -> List[str]:
        return ["begin_simulation, simulation_sync_achieved"]

    def GetFeatureValues(self) -> List[Any]:
        return self._time

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_name == "begin_simulation":
            self._sim_start_time = event.timestamp
        elif event.event_name == "simulation_sync_achieved":
            self._time = event.timestamp - self._sim_start_time
