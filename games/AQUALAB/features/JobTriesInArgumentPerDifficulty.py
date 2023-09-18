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


class JobTriesInArgumentPerDifficulty(PerDifficultyFeature):
    
    def __init__(self, params:ExtractorParameters, diff_map:dict, difficulty_type:Optional[str]):
        super().__init__(params=params, diff_map=diff_map, difficulty_type=difficulty_type)
        self._count = 0
        self._found = False

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["begin_argument", "bestiary_select_species", "bestiary_select_environment", "bestiary_select_model", "complete_argument"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        # if event.EventName == "begin_argument":
        #     self._found = True
        #     return
        # if event.EventName == "complete_argument":
        #     self._found = False
        #     return
        # if not self._found:
        #     return
        self._count +=1
        #print("over here!")
    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        print(self._count)
        return [self._count]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "0"
