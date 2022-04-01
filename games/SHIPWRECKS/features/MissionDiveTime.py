# import libraries
from datetime import timedelta
from typing import Any, List, Union
# import locals
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class MissionDiveTime(Feature):
    
    def __init__(self, name:str, description:str, job_num:int, job_map:dict):
        super().__init__(name=name, description=description, count_index=job_num)
        self._dive_start_time = None
        self._time = timedelta(0)

    # *** Implement abstract functions ***
    def _getEventDependencies(self) -> List[str]:
        return ["dive_start", "dive_exit"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_name == "dive_start":
            self._dive_start_time = event.timestamp
        elif event.event_name == "dive_exit":
            if self._dive_start_time is not None:
                self._time += (event.timestamp - self._dive_start_time).total_seconds()
                self._dive_start_time = None

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._time]

    # *** Optionally override public functions. ***
