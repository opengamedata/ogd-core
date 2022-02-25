# Global imports
import logging
from typing import Any, List, Union
from statistics import stdev
# Local imports
import utils
from extractors.Feature import Feature
from schemas.Event import Event

class JobsAttempted(Feature):

    def __init__(self, name:str, description:str, job_num:int, job_map:dict):
        self._job_num = job_num
        self._job_map = job_map
        super().__init__(name=name, description=description, count_index=job_num)
        # Subfeatures
        self._job_id = None
        self._job_name = None
        self._num_starts = 0
        self._num_completes = 0
        self._percent_complete = 0
        self._avg_time_complete = 0
        self._std_dev_complete = 0

        # Time
        self._times = []
        self._job_start_time = None

    def GetEventTypes(self) -> List[str]:
        return ["accept_job", "complete_job"]

    def Subfeatures(self) -> List[str]:
        return ["job-name", "num-starts", "num-completes", "percent-complete", "avg-time-complete", "std-dev-complete"]

    def GetFeatureValues(self) -> List[Any]:
        return [self._job_id, self._job_name, self._num_starts, self._num_completes, self._percent_complete, self._avg_time_complete, self._std_dev_complete]

    def MinVersion(self) -> Union[str,None]:
        return "2"

    def _extractFromEvent(self, event:Event) -> None:
        if self._validate_job(event.event_data["job_id"]):
            if not self._job_id and not self._job_name:
                self._job_id = event.event_data["job_id"]["int_value"]
                self._job_name = event.event_data["job_name"]["string_value"]

            if event.event_name == "accept_job" and self._job_id == self._job_num:
                self._job_start_time = event.timestamp
                self._num_starts += 1

            elif event.event_name == "complete_job" and self._job_id == self._job_num:
                self._num_completes += 1

                if self._job_start_time:
                    self._times.append((event.timestamp - self._job_start_time).total_seconds())
                    self._avg_time_complete = sum(self._times) / len(self._times)
                    self._job_start_time = None

            self._percent_complete = (self._num_completes / (self._num_completes + self._num_starts)) * 100
                
            if len(self._times) > 1:
                self._std_dev_complete = stdev(self._times)

    def _validate_job(self, job_data):
        ret_val : bool = False
        if job_data['int_value'] is not None:
            if job_data['int_value'] == self._count_index:
                ret_val = True
        elif job_data['string_value'] is not None:
            if self._job_map[job_data['string_value']] == self._count_index:
                ret_val = True
        else:
            utils.Logger.toStdOut(f"Got invalid job_id data in JobsAttempted", logging.WARNING)
        return ret_val