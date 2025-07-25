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

class JobQuitsPerComplete(Feature):

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
    
    def _updateFromFeatureData(self, feature:FeatureData):
        if feature.ExportMode == self.ExtractionMode:
            if feature.Name == "TotalJobQuits":
                self._total_job_quits = feature.FeatureValues[0]
            elif feature.Name == "JobsCompleted":
                self._jobs_completed = feature.FeatureValues[0]

    def _getFeatureValues(self) -> List[Any]:
        if self._jobs_completed != 0:
            value = self._total_job_quits / self._jobs_completed
        else:
            value = 0
        return [value]

    # *** Optionally override public functions. ***
