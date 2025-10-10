# import libraries
import logging
from typing import Any, List, Optional
# import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.games.AQUALAB.features.PerDifficultyFeature import PerDifficultyFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature


class JobTriesInArgumentPerDifficulty(PerDifficultyFeature):
    
    def __init__(self, params:GeneratorParameters, diff_map:dict, difficulty_type:Optional[str]):
        super().__init__(params=params, diff_map=diff_map, difficulty_type=difficulty_type)
        self._count = 0
        self._found = False

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["begin_argument", "bestiary_select_species", "bestiary_select_environment", "bestiary_select_model", "complete_argument"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        self._count += 1
        #print("over here!")
    def _updateFromFeature(self, feature:Feature):
        return

    def _getFeatureValues(self) -> List[Any]:
        print(self._count)
        return [self._count]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "3"
