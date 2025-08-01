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

class TotalJobQuits(Extractor):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._total_count = 0
        self._non_whale_count = 0

    def Subfeatures(self) -> List[str]:
        return ["NonArcticMissingWhale"]
    
    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["accept_job"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        leaving_job = event.GameState.get("job_name")
        if leaving_job != "no-active-job":
            self._total_count += 1
            if leaving_job != "arctic-missing-whale":
                self._non_whale_count += 1

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._total_count, self._non_whale_count] 

    # *** Optionally override public functions. ***
