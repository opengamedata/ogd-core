# import libraries
from collections import defaultdict
from statistics import stdev
from typing import Any, List
# import locals
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData


class JobsAttempted(Feature):

    def __init__(self, params:GeneratorParameters, mission_map:dict):
        self._mission_map = mission_map
        super().__init__(params=params)
        self._session_id = None
        self._start_map = defaultdict(list)
        self._complete_map = defaultdict(list)

        # Subfeatures
        if self.CountIndex is not None:
            self._mission_id = self.CountIndex
            self._mission_name = list(mission_map.keys())[self.CountIndex]
        else:
            raise ValueError("JobsAttempted got a count index of None!")
        self._num_starts = 0
        self._num_completes = 0
        self._percent_complete = 0
        self._avg_time_complete = 0
        self._std_dev_complete = 0

        # Time
        self._times = []
        self._mission_start_time = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["checkpoint"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        session_id = event.SessionID
        checkpoint = event.EventData["status"]
        mission_name = event.EventData["mission_id"]
        mission_id = self._mission_map[mission_name]

        if checkpoint == "Begin Mission":
            if mission_name == "Level4" and session_id not in self._complete_map[2]:
                return
            elif mission_id == self._mission_id and session_id not in self._start_map[mission_id]:
                self._num_starts += 1
                self._session_id = session_id
                self._mission_start_time = event.Timestamp
                self._start_map[mission_id].append(session_id)
                self._session_id = session_id

        elif checkpoint == "Case Closed":
            self._complete_map[mission_id].append(session_id)

            if mission_id == self._mission_id and session_id == self._session_id:
                self._num_completes += 1
                self._complete_map[mission_id].append(session_id)

                if self._mission_start_time:
                    self._times.append((event.Timestamp - self._mission_start_time).total_seconds())
                    self._mission_start_time = None

    def _updateFromFeatureData(self, feature:FeatureData):
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
