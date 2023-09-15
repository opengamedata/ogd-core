# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from utils.Logger import Logger
from extractors.Extractor import ExtractorParameters
from games.AQUALAB.features.PerJobFeature import PerJobFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData

class JobHelpCount(PerJobFeature):

    def __init__(self, params:ExtractorParameters, job_map:dict):
        self._job_map = job_map
        super().__init__(params=params, job_map=job_map)
        self._by_task       : Dict[str, int] = {}
        self._current_count : int = 0
        self._total_count   : int = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["ask_for_help", "complete_task"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventName == "ask_for_help":
            self._current_count += 1
            self._total_count += 1
        elif event.EventName == "complete_task":
            task_id = event.EventData.get("task_id", "UNKNOWN_TASK")
            self._by_task[task_id] = self._current_count
            self._current_count = 0

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._total_count, self._by_task]

    # *** Optionally override public functions. ***

    def Subfeatures(self) -> List[str]:
        return ["ByTask"]

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
