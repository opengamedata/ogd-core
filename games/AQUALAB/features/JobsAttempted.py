# import libraries
import logging
from datetime import datetime
from statistics import stdev
from typing import Any, List, Optional
# import locals
from utils import Logger
from extractors.Extractor import ExtractorParameters
from extractors.features.Feature import Feature
from schemas.Event import Event
from schemas.FeatureData import FeatureData

class JobsAttempted(Feature):

    def __init__(self, params:ExtractorParameters, job_map:dict, diff_map: dict):
        self._job_map = job_map
        super().__init__(params=params)
        self._user_code = None
        self._session_id = None

        # Subfeatures
        if self.CountIndex is not None:
            self._job_id = self.CountIndex
            self._job_name = list(job_map.keys())[self.CountIndex]
            self._difficulties = diff_map[self.CountIndex]
        else:
            raise ValueError("JobsAttempted was not given a count index!")
        self._num_starts = 0
        self._num_completes = 0
        self._percent_complete = 0
        self._avg_time_complete = 0
        self._std_dev_complete = 0

        # Time
        self._times = []
        self._time = 0
        self._job_start_time : Optional[datetime] = None
        self._prev_timestamp : Optional[datetime] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["accept_job", "complete_job"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.SessionID != self._session_id:
            self._session_id = event.SessionID

            if self._job_start_time is not None and self._prev_timestamp is not None:
                self._time += (self._prev_timestamp - self._job_start_time).total_seconds()
                self._job_start_time = event.Timestamp

        if self._validate_job(event.EventData['job_name']):
            user_code = event.UserID
            job_name = event.EventData["job_name"]["string_value"]
            job_id = self._job_map[job_name]

            if event.EventName == "accept_job" and job_id == self._job_id:
                self._num_starts += 1
                self._user_code = user_code
                self._job_start_time = event.Timestamp

            elif event.EventName == "complete_job" and job_id == self._job_id and user_code == self._user_code:
                self._num_completes += 1

                if self._job_start_time:
                    self._time += (event.Timestamp - self._job_start_time).total_seconds()
                    self._times.append(self._time)
                    self._time = 0
                    self._job_start_time = None

        self._prev_timestamp = event.Timestamp

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if self._num_starts > 0:
            self._percent_complete = (self._num_completes / self._num_starts) * 100

        if self._time != 0:
            self._times.append(self._time)
        
        if len(self._times) > 0:
            self._avg_time_complete = sum(self._times) / len(self._times)

        if len(self._times) > 1:
            self._std_dev_complete = stdev(self._times)

        return [self._job_id, self._job_name, self._num_starts, self._num_completes, self._percent_complete, self._avg_time_complete, self._std_dev_complete, self._difficulties]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["job-name", "num-starts", "num-completes", "percent-complete", "avg-time-complete", "std-dev-complete", "job-difficulties"]

    def MinVersion(self) -> Optional[str]:
        return "1"

    # *** Other local functions
    def _validate_job(self, job_data):
        ret_val : bool = False
        if job_data['string_value'] and job_data['string_value'] in self._job_map:
            ret_val = True
        else:
            Logger.Log(f"Got invalid job_name data in JobsAttempted", logging.WARNING)
        return ret_val
