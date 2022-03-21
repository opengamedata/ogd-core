from statistics import stdev
from typing import Any, List, Union

from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class MissionsAttempted(Feature):

    def __init__(self, name:str, description:str, job_num:int, job_map:dict):
        self._job_map = job_map
        super().__init__(name=name, description=description, count_index=job_num)
        self._user_code = None

        # Subfeatures
        self._mission_id = job_num
        self._num_starts = 0
        self._num_completes = 0
        self._percent_complete = 0
        self._avg_time_complete = 0
        self._std_dev_complete = 0

        # Time
        self._times = []
        self._job_start_time = None

    def GetEventDependencies(self) -> List[str]:
        return ["mission_start", "mission_complete"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def Subfeatures(self) -> List[str]:
        return ["mission-id", "num-starts", "num-completes", "percent-complete", "avg-time-complete", "std-dev-complete"]

    def GetFeatureValues(self) -> List[Any]:
        if self._num_starts > 0:
            self._percent_complete = (self._num_completes / self._num_starts) * 100
        
        if len(self._times) > 0:
            self._avg_time_complete = sum(self._times) / len(self._times)

        if len(self._times) > 1:
            self._std_dev_complete = stdev(self._times)

        return [self._mission_id, self._num_starts, self._num_completes, self._percent_complete, self._avg_time_complete, self._std_dev_complete]

    def MinVersion(self) -> Union[str,None]:
        return "1"

    def _extractFromEvent(self, event:Event) -> None:
        user_code = event.user_id
        mission_id = event.event_data["mission_id"]["int_value"]

        if event.event_name == "mission_start" and mission_id == self._mission_id:
            self._num_starts += 1
            self._user_code = user_code
            self._job_start_time = event.timestamp

        elif event.event_name == "mission_complete" and mission_id == self._mission_id and user_code == self._user_code:
            self._num_completes += 1

            if self._job_start_time:
                self._times.append((event.timestamp - self._job_start_time).total_seconds())
                self._job_start_time = None

    def _extractFromFeatureData(self, feature: FeatureData):
        return
