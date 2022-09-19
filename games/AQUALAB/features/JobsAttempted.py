# import libraries
import logging
from datetime import datetime, timedelta
from statistics import stdev
from typing import Any, List, Optional
from schemas.ExtractionMode import ExtractionMode
# import locals
from utils import Logger
from extractors.Extractor import ExtractorParameters
from extractors.features.Feature import Feature
from schemas.Event import Event
from schemas.FeatureData import FeatureData

class JobsAttempted(Feature):

    def __init__(self, params:ExtractorParameters, job_map:dict, diff_map: dict):
        self._pop_call_count = 0
        self._pla_call_count = 0
        self._ses_call_count = 0
        self._player_id = None

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
        self._times : List[int] = []
        # self._time = 0
        self._job_start_time : Optional[datetime] = None
        self._prev_timestamp : Optional[datetime] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["accept_job", "complete_job"]

    def _getFeatureDependencies(self) -> List[str]:
        return ["JobActiveTime"]

    def _extractFromEvent(self, event:Event) -> None:
        if event.UserID != self._player_id:
            self._player_id = event.UserID
        if event.SessionID != self._session_id:
            self._session_id = event.SessionID

            if self._job_start_time is not None and self._prev_timestamp is not None:
                # self._time += (self._prev_timestamp - self._job_start_time).total_seconds()
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
                    # self._time += (event.Timestamp - self._job_start_time).total_seconds()
                    # self._times.append(self._time)
                    # self._time = 0
                    self._job_start_time = None

        self._prev_timestamp = event.Timestamp

    def _extractFromFeatureData(self, feature:FeatureData):
        if feature.ExportMode == ExtractionMode.POPULATION:
            self._pop_call_count += 1
        if feature.ExportMode == ExtractionMode.PLAYER:
            self._pla_call_count += 1
        if feature.ExportMode == ExtractionMode.SESSION:
            self._ses_call_count += 1

        if feature.FeatureType == "JobActiveTime":
            if feature.CountIndex == self.CountIndex:
                if self.ExportMode    == ExtractionMode.SESSION \
            and feature.ExportMode == ExtractionMode.SESSION:
                    # session should only have one time, namely the time for the session.
                    self._times = [feature.FeatureValues[0]]
                elif self.ExportMode == ExtractionMode.PLAYER \
                and feature.ExportMode == ExtractionMode.PLAYER:
                    # player should only have one time, namely the time for the player.
                    self._times = [feature.FeatureValues[0]]
                elif self.ExportMode == ExtractionMode.POPULATION \
                and feature.ExportMode == ExtractionMode.PLAYER:
                    # population should only have one time, namely the time for the player.
                    self._times.append(feature.FeatureValues[0])

    def _getFeatureValues(self) -> List[Any]:
        total_ct = self._pop_call_count + self._pla_call_count + self._ses_call_count
        count_str = f"{total_ct} times ({self._pop_call_count}, {self._pla_call_count}, {self._ses_call_count})"
        # temp
        if self.CountIndex == 0:
            if self.ExportMode == ExtractionMode.POPULATION:
                Logger.Log(f"{self.Name} was called {count_str} in pop mode")
            if self.ExportMode == ExtractionMode.PLAYER:
                Logger.Log(f"{self.Name} was called {count_str} in player mode for player {self._player_id}")
            if self.ExportMode == ExtractionMode.SESSION:
                Logger.Log(f"{self.Name} was called {count_str} in session mode for player {self._player_id}, session {self._session_id}")

        if self._num_starts > 0:
            self._percent_complete = (self._num_completes / self._num_starts) * 100

        # if self._time != 0:
        #     self._times.append(self._time)
        
        if len(self._times) > 0:
            self._avg_time_complete = sum(self._times) / len(self._times)

        if len(self._times) > 1:
            self._std_dev_complete = stdev(self._times)

        return [self._job_id, self._job_name, self._num_starts, self._num_completes, self._percent_complete, self._avg_time_complete, self._std_dev_complete, self._difficulties]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["job-name", "num-starts", "num-completes", "percent-complete", "avg-time-per-attempt", "std-dev-per-attempt", "job-difficulties"]

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"

    # *** Other local functions
    def _validate_job(self, job_data):
        ret_val : bool = False
        if job_data['string_value'] and job_data['string_value'] in self._job_map:
            ret_val = True
        else:
            Logger.Log(f"Got invalid job_name data in JobsAttempted", logging.WARNING)
        return ret_val
