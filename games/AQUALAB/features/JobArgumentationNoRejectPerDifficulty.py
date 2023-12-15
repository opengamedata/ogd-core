# import libraries
import logging
from typing import Any, List, Optional
from games.AQUALAB.features.PerDifficultyFeature import PerDifficultyFeature
# import locals
from utils.Logger import Logger
from extractors.Extractor import ExtractorParameters
from games.AQUALAB.features.PerJobFeature import PerJobFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData


class JobArgumentationNoRejectPerDifficulty(PerDifficultyFeature):
    
    def __init__(self, params:ExtractorParameters, diff_map:dict, difficulty_type:Optional[str]):
        super().__init__(params=params, diff_map=diff_map, difficulty_type=difficulty_type)
        self._complete_argument = False
        self._fact_rejected_found = False

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["fact_rejected", "fact_submitted", "complete_argument"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventName == "complete_argument":
            self._complete_argument = True
        if event.EventName == "fact_rejected":
            self._fact_rejected_found = True
    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if(self._complete_argument == True and self._fact_rejected_found == False):
            return [1]
        elif(self._complete_argument == True and self._fact_rejected_found == True):
            return [0]
        else:
            return [-1]
    
    # *** Optionally override public functions. ***
    @staticmethod       
    def MinVersion() -> Optional[str]:
        return