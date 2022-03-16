# Global imports
import logging
from datetime import timedelta
from typing import Any, List
# Local imports
import utils
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class TotalDiveTime(Feature):
    
    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0)
        self._dive_start_time = None
        self._time = timedelta(0)

    def GetEventDependencies(self) -> List[str]:
        return ["begin_dive", "scene_changed"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_name == "begin_dive":
            self._dive_start_time = event.timestamp
        elif event.event_name == "scene_changed":
            if self._dive_start_time is not None:
                self._time += event.timestamp - self._dive_start_time
                self._dive_start_time = None
            else:
                utils.Logger.Log("Scene changed when we had no active start time!", logging.WARNING)

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def GetFeatureValues(self) -> List[Any]:
        return [self._time]
