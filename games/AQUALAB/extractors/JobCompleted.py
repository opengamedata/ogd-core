from datetime import timedelta
from typing import Any, List

from extractors.Feature import Feature
from schemas.Event import Event

class JobCompleted(Feature):

    def __init__(self, name:str, description:str, job_num:int, job_map:dict):
        self._job_map = job_map
        super().__init__(name=name, description=description, count_index=job_num)
        self._completed = False

    def GetEventTypes(self) -> List[str]:
        return ["complete_job"]

    def CalculateFinalValues(self) -> Any:
        return self._completed

    def _extractFromEvent(self, event:Event) -> None:
        if self._job_map[event.event_data["job_id"]['string_value']] == self._count_index:
            self._completed = True
