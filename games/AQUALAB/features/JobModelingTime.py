# import libraries
import logging
from datetime import timedelta
from typing import Any, List
# import locals
from utils import Logger
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class JobModelingTime(Feature):
    def __init__(self, name:str, description:str, job_num:int, job_map:dict):
        self._job_map = job_map
        super().__init__(name=name, description=description, count_index=job_num)
        self._modeling_start_time = None
        self._time = timedelta(0)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return []

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_name == "begin_modeling":
            self._modeling_start_time = event.timestamp
        elif event.event_name == "room_changed":
            if self._modeling_start_time is not None:
                self._time += event.timestamp - self._modeling_start_time
                self._modeling_start_time = None

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._time]

    # *** Optionally override public functions. ***
