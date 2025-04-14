# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.games.AQUALAB.features.PerJobFeature import PerJobFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

class JobStarted(PerJobFeature):

    def __init__(self, params:GeneratorParameters, job_map:dict):
        self._job_map = job_map
        super().__init__(params=params, job_map=job_map)
        self._job_started = False
        self._job_accept_count = 0
        self._switch_job_count = 0

    def Subfeatures(self) -> List[str]:
        return ["Count"]
    
    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["accept_job", "switch_job"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if event.EventName == "accept_job":
                self._job_started = True
                self._job_accept_count += 1
    
        elif event.EventName == "switch_job":
            new_job = event.GameState.get("job_name")
            if new_job == self.TargetJobName:
                self._switch_job_count += 1

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._job_started, self._job_accept_count + self._switch_job_count] 

    # *** Optionally override public functions. ***
