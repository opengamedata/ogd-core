# import libraries
import logging
from typing import Any, List, Optional
# import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.games.AQUALAB.features.PerJobFeature import PerJobFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData


class JobArgumentationFails(PerJobFeature):
    
    #CASE A: n_complete > n_leave
        # return 0
    # CASE B: 1 complete, 1 leave arguments:
        # return 1(diff + 1)
    # CASE C: n_complete < n_leave:
        # return n_leave + 1 - n_complete


    def __init__(self, params:GeneratorParameters, job_map:dict):
        super().__init__(params=params, job_map=job_map)
        self._leave_count = 0
        self._found = False
        self._success_count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["leave_argument", "complete_argument"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if(event.EventName == "leave_argument"):
            self._leave_count += 1
        if(event.EventName == "complete_argument"):
            self._success_count += 1
    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if(self._success_count > self._leave_count):
            return [0]
        else:
            return [(self._leave_count + 1) - self._success_count]
        


    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return
