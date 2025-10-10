# import libraries
import logging
from typing import Any, List, Optional
# import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.games.AQUALAB.features.PerJobFeature import PerJobFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature


class JobArgumentationSuccessRatio(PerJobFeature):
    
    def __init__(self, params:GeneratorParameters, job_map:dict):
        super().__init__(params=params, job_map=job_map)
        self._fact_reject = 0
        self._fact_submit = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["fact_rejected", "fact_submitted"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if event.EventName == "fact_rejected":
            self._fact_reject += 1
        if event.EventName == "fact_submitted":
            self._fact_submit +=1
    def _updateFromFeature(self, feature:Feature):
        return

    def _getFeatureValues(self) -> List[Any]:
        if(self._fact_reject == 0 and self._fact_submit != 0):
            return [1]
        if(self._fact_submit == 0):
            return [0]
        return [self._fact_reject / self._fact_submit]
        

    # *** Optionally override public functions. ***
    @staticmethod       
    def MinVersion() -> Optional[str]:
        return
