from datetime import timedelta
from typing import Any, List

from extractors.Feature import Feature
from schemas.Event import Event

class JobExperimentationTime(Feature):

    def __init__(self, name:str, description:str, job_num:int, job_map:dict):
        self._job_map = job_map
        super().__init__(name=name, description=description, count_index=job_num)
        self._experiment_start_time = None
        self._time = timedelta(0)

    def GetEventTypes(self) -> List[str]:
        return ["begin_experiment", "room_changed"]

    def GetFeatureValues(self) -> List[Any]t[Any]:
        return self._time

    def _extractFromEvent(self, event:Event) -> None:
        if self._validate_job(event.event_data['job_id']):
            if event.event_name == "begin_experiment":
                self._experiment_start_time = event.timestamp
            elif event.event_name == "room_changed":
                self._time += event.timestamp - self._experiment_start_time
                self._experiment_start_time = None

    def _validate_job(self, job_data):
        ret_val : bool = False
        if job_data['int_value'] is not None:
            if job_data['int_value'] == self._count_index:
                ret_val = True
        elif job_data['string_value'] is not None:
            if self._job_map[job_data['string_value']] == self._count_index:
                ret_val = True
        else:
            print(f"Got invalid job_id data in JobStartCount")
        return ret_val
