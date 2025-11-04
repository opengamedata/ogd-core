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


class JobArgumentationNoReject(PerJobFeature):
    
    def __init__(self, params:GeneratorParameters, job_map:dict):
        super().__init__(params=params, job_map=job_map)
        self._complete_argument = False
        self._fact_rejected_found = False

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["all_events"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        #print(event.EventName)
        if event.EventName == "complete_argument":
            self._complete_argument = True
        if event.EventName == "fact_rejected":
            self._fact_rejected_found = True
    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if(self._complete_argument == True and self._fact_rejected_found == False):
            return [1]
        elif(self._complete_argument == True and self._fact_rejected_found == True):
            return [-1]
        else:
            return [0]
    
    # *** Optionally override public functions. ***
    @staticmethod       
    def MinVersion() -> Optional[str]:
        return