# Global imports
import logging
from datetime import timedelta
from typing import Any, List
# Local imports
import utils
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class TotalArgumentationTime(Feature):
    
    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0)
        self._argue_start_time = None
        self._time = timedelta(0)

    def GetEventDependencies(self) -> List[str]:
        return ["begin_argument", "room_changed"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        return [self._time]

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_name == "begin_argument":
            self._argue_start_time = event.timestamp
        elif event.event_name == "room_changed":
            if self._argue_start_time is not None:
                self._time += event.timestamp - self._argue_start_time
                self._argue_start_time = None
            else:
                utils.Logger.Log("Room changed when we had no active start time!", logging.WARNING)

    def _extractFromFeatureData(self, feature: FeatureData):
        return
