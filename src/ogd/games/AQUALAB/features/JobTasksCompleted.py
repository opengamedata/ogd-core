# import libraries
import logging
from collections import Counter
from typing import Any, List, Optional, Union
# import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.games.AQUALAB.features.PerJobFeature import PerJobFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

class JobTasksCompleted(PerJobFeature):
    
    def __init__(self, params:GeneratorParameters, job_map:dict):
        super().__init__(params=params, job_map=job_map)
        self._completed_tasks = []
        self._task_counter    = Counter()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["complete_task"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        _task = event.EventData.get("task_id", "TASK NAME NOT FOUND")
        if _task in self._completed_tasks:
            Logger.Log(f"Player {event.UserID} repeated task {_task} in job {event.GameState.get("job_name")}!", logging.WARN)
        match self.ExtractionMode:
            case ExtractionMode.POPULATION:
                self._task_counter[_task] += 1
            case ExtractionMode.PLAYER | ExtractionMode.SESSION:
                self._completed_tasks.append(_task)
            case _:
                raise ValueError(f"JobTasksCompleted was given an invalid extraction mode of {self.ExtractionMode}!")

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        _base_val = self._task_counter         if self.ExtractionMode == ExtractionMode.POPULATION else self._completed_tasks
        _count    = self._task_counter.total() if self.ExtractionMode == ExtractionMode.POPULATION else len(self._completed_tasks)
        return [_base_val, len(self._completed_tasks)]

    def Subfeatures(self) -> List[str]:
        return ["Count"]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"