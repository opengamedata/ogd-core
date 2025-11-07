# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.games.AQUALAB.features.PerJobFeature import PerJobFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature

class JobQuitsPerComplete(Extractor):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._total_job_quits = 0
        self._jobs_completed = 0

    def Subfeatures(self) -> List[str]:
        return []
    
    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["TotalJobQuits", "JobsCompleted"]

    def _updateFromEvent(self, event:Event) -> None:
        return 
    
    def _updateFromFeature(self, feature:Feature):
        if feature.ExportMode == self.ExtractMode:
            if feature.Name == "TotalJobQuits":
                self._total_job_quits = feature.Values[0]
            elif feature.Name == "JobsCompleted":
                self._jobs_completed = feature.Values[1]

    def _getFeatureValues(self) -> List[Any]:
        if self._jobs_completed != 0:
            value = self._total_job_quits / self._jobs_completed
        else:
            value = 0
        return [value]

    # *** Optionally override public functions. ***
