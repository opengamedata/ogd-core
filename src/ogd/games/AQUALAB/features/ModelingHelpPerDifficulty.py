# import libraries
from datetime import datetime, timedelta
import logging, warnings
from typing import Any, List, Optional
from ogd.games.AQUALAB.features.PerDifficultyFeature import PerDifficultyFeature
# import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from extractors.features.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData


class ModelingHelpPerDifficulty(PerDifficultyFeature):

    def __init__(self, params:GeneratorParameters, diff_map:dict, difficulty_type:Optional[str]):
        super().__init__(params=params, diff_map=diff_map, difficulty_type=difficulty_type)
        self._found = False
        self._help = False
        

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["ask_for_help", "begin_model"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if(event.EventName == "begin_model"):
            self._found = True
        if(self._found == True and event.EventName == "ask_for_help"):
            self._help = True

        

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if(self._help == True):
            return [1]
        else:
            return [0]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "3"
