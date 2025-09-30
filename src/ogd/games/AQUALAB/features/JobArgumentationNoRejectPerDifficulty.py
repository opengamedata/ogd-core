# import libraries
import logging
from typing import Any, List, Optional
from ogd.games.AQUALAB.features.PerDifficultyFeature import PerDifficultyFeature
# import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.games.AQUALAB.features.PerJobFeature import PerJobFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData


class JobArgumentationNoRejectPerDifficulty(PerDifficultyFeature):
    
    def __init__(self, params:GeneratorParameters, diff_map:dict, difficulty_type:Optional[str]):
        super().__init__(params=params, diff_map=diff_map, difficulty_type=difficulty_type)
        self._complete_argument = False
        self._fact_rejected_found = False

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["fact_rejected", "fact_submitted", "complete_argument"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
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
            return [0]
        else:
            return [-1]
    
    # *** Optionally override public functions. ***
    @staticmethod       
    def MinVersion() -> Optional[str]:
        return