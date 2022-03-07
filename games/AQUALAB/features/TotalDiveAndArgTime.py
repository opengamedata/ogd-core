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
        self._dive_time = timedelta()
        self._arg_time = timedelta()

    def GetEventDependencies(self) -> List[str]:
        return []

    def GetFeatureDependencies(self) -> List[str]:
        return ["TotalDiveTime", "TotalArgumentationTime"]

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        if feature.Name() == "TotalDiveTime" and feature.SessionID() is not None:
            self._dive_time = feature.FeatureValues()[0]
        elif feature.Name() == "TotalArgumentationTime" and feature.SessionID() is not None:
            self._arg_time = feature.FeatureValues()[0]

    def GetFeatureValues(self) -> List[Any]:
        return [self._dive_time + self._arg_time]
