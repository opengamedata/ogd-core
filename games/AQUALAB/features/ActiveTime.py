# import libraries
from datetime import datetime, timedelta
import logging, warnings
from typing import Any, List, Optional
# import locals
from utils import Logger
from extractors.Extractor import ExtractorParameters
from extractors.features.Feature import Feature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData

class ActiveTime(Feature):
    IDLE_LEVEL = 30

    def __init__(self, params:ExtractorParameters, job_map:dict, active_threads:float = None):
        self._job_map = job_map
        super().__init__(params=params)
        self._Idle_time: float = 0
        self.active_level:float = active_threads if active_threads else ActiveTime.IDLE_LEVEL
        self._sess_duration: Optional[timedelta] = None
        

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["Idle"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["SessionDuration"]

    def _extractFromEvent(self, event:Event) -> None:
        if not self.active_level:
            self.active_level = event.EventData.get("level")
        else:
            if self.active_level != event.EventData.get("level"):
                warnings.warn("The idle event has a different threshold!")
                return
        self._Idle_time += event.EventData.get("time")
        

    def _extractFromFeatureData(self, feature:FeatureData):
        self._sess_duration = feature.FeatureValues[0]
        return

    def _getFeatureValues(self) -> List[Any]:
        if self._sess_duration == "No events":
            return ["No events"]
        return [self._sess_duration - timedelta(seconds=self._Idle_time)]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
