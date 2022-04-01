# import libraries
from statistics import stdev
from typing import Any, List
# import locals
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class JobsAttempted(Feature):

    def __init__(self, name:str, description:str, mission_num:int, mission_map:dict):
        self._mission_map = mission_map
        super().__init__(name=name, description=description, count_index=mission_num)
        self._session_id = None

        # Subfeatures
        self._mission_id = mission_num
        self._mission_name = list(mission_map.keys())[mission_num]
        self._num_starts = 0
        self._num_completes = 0
        self._percent_complete = 0
        self._avg_time_complete = 0
        self._std_dev_complete = 0

        # Time
        self._times = []
        self._mission_start_time = None

    # *** Implement abstract functions ***
    def _getEventDependencies(self) -> List[str]:
        return ["checkpoint"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        session_id = event.session_id
        checkpoint = event.event_data["status"]["string_value"]
        mission_name = event.event_data["mission_id"]["string_value"]
        mission_id = self._mission_map[mission_name]

        if checkpoint == "Begin Mission" and mission_id == self._mission_id:
            self._num_starts += 1
            self._session_id = session_id
            self._mission_start_time = event.timestamp

        elif checkpoint == "Case Closed" and mission_id == self._mission_id and session_id == self._session_id:
            self._num_completes += 1

            if self._mission_start_time:
                self._times.append((event.timestamp - self._mission_start_time).total_seconds())
                self._mission_start_time = None

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if self._num_starts > 0:
            self._percent_complete = (self._num_completes / self._num_starts) * 100
        
        if len(self._times) > 0:
            self._avg_time_complete = sum(self._times) / len(self._times)

        if len(self._times) > 1:
            self._std_dev_complete = stdev(self._times)

        return [self._mission_id, self._mission_name, self._num_starts, self._num_completes, self._percent_complete, self._avg_time_complete, self._std_dev_complete]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["job-name", "num-starts", "num-completes", "percent-complete", "avg-time-complete", "std-dev-complete"]
