from datetime import datetime, timedelta
from typing import Any, List, Union

from extractors.Feature import Feature
from schemas.Event import Event

class JobArgumentationTime(Feature):

    def __init__(self, name:str, description:str, job_num:int, job_map:dict):
        self._job_map = job_map
        super().__init__(name=name, description=description, count_index=job_num)
        self._argument_start_time : Union[datetime, None] = None
        self._time = timedelta(0)

    def GetEventTypes(self) -> List[str]:
        return ["begin_argument", "room_changed"]

    def CalculateFinalValues(self) -> Any:
        return self._time

    def _extractFromEvent(self, event:Event) -> None:
        if self._job_map[event.event_data["job_id"]['string_value']] == self._count_index:
            if event.event_name == "begin_argument":
                self._argument_start_time = event.timestamp
            elif event.event_name == "room_changed" and self._argument_start_time is not None:
                self._time += event.time_offset - self._argument_start_time
                self._argument_start_time = None
