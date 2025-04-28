# import libraries
from typing import Any, List, Optional
# import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.games.AQUALAB.features.PerJobFeature import PerJobFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

class LeftJob(PerJobFeature):
    def __init__(self, params:GeneratorParameters, job_map:dict):
        super().__init__(params=params, job_map=job_map)
        self._left_job = False
        self._job_started = False
        self._switch_count = 0
        self._complete_count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["accept_job", "switch_job", "complete_job"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if event.EventName == "accept_job":
            self._job_started = True
            self._left_job = False 
        elif event.EventName == "switch_job":
            old_job = event.EventData.get("prev_job_name")
            if old_job == self.TargetJobName:
                self._switch_count += 1
        elif event.EventName == "complete_job":
            completed_job = event.GameState.get("job_name")
            if completed_job == self.TargetJobName:
                self._complete_count += 1
                
    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._switch_count - self._complete_count]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
