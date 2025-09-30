# import libraries
import logging
from typing import Any, List, Optional
# import locals
from utils.Logger import Logger
from extractors.Extractor import ExtractorParameters
from games.AQUALAB.features.PerDifficultyFeature import PerDifficultyFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData


class JobArgumentationSuccessRatioPerDifficulty(PerDifficultyFeature):
    
    def __init__(self, params:ExtractorParameters, diff_map:dict, difficulty_type:Optional[str]):
        super().__init__(params=params, diff_map=diff_map, difficulty_type=difficulty_type)
        self._fact_reject = 0
        self._fact_submit = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["fact_rejected", "fact_submitted"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventName == "fact_rejected":
            self._fact_reject += 1
        if event.EventName == "fact_submitted":
            self._fact_submit +=1
    def _extractFromFeatureData(self, feature:FeatureData):
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
        return "3"
