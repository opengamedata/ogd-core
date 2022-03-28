from datetime import timedelta
from typing import Any, List, Union

from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class MissionSonarTimeToComplete(Feature):
    
    def __init__(self, name:str, description:str, job_num:int, job_map:dict):
        super().__init__(name=name, description=description, count_index=job_num)
        self._sonar_start_time = None
        self._time = timedelta(0)

    def GetEventDependencies(self) -> List[str]:
        return ["sonar_start", "sonar_exit"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        return [self._time]

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_name == "sonar_start":
            self._sonar_start_time = event.timestamp
        elif event.event_name == "sonar_complete":
            if self._sonar_start_time is not None:
                self._time += (event.timestamp - self._sonar_start_time).total_seconds()
                self._sonar_start_time = None

    def _extractFromFeatureData(self, feature: FeatureData):
        return
