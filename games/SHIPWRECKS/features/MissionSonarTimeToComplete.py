# import libraries
from datetime import timedelta
from typing import Any, List, Union
# import locals
from features.Feature import Feature
from schemas.FeatureData import FeatureData
from schemas.Event import Event

class MissionSonarTimeToComplete(Feature):
    
    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def __init__(self, name:str, description:str, job_num:int, job_map:dict):
        super().__init__(name=name, description=description, count_index=job_num)
        self._sonar_start_time = None
        self._time = timedelta(0)

    def _getEventDependencies(self) -> List[str]:
        return ["sonar_start", "sonar_exit"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_name == "sonar_start":
            self._sonar_start_time = event.timestamp
        elif event.event_name == "sonar_complete":
            if self._sonar_start_time is not None:
                self._time += (event.timestamp - self._sonar_start_time).total_seconds()
                self._sonar_start_time = None

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._time]

    # *** Optionally override public functions. ***