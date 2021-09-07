from typing import Any, List

from extractors.Feature import Feature
from schemas.Event import Event

class JobHelpCount(Feature):

    def __init__(self, name:str, description:str, job_num:int, job_map:dict):
        self._job_map = job_map
        super().__init__(name=name, description=description, count_index=job_num)
        self._count = 0

    def GetEventTypes(self) -> List[str]:
        return ["ask_for_help"]

    def CalculateFinalValues(self) -> Any:
        return self._count

    def _extractFromEvent(self, event:Event) -> None:
        if self._job_map[event.event_data["job_id"]] == self._count_index:
            self._count += 1
