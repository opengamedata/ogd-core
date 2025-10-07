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


class ModelPredictCountPerDifficulty(PerDifficultyFeature):

    def __init__(self, params:GeneratorParameters, diff_map:dict, difficulty_type:Optional[str]):
        super().__init__(params=params, diff_map=diff_map, difficulty_type=difficulty_type)
        self._count = 0
        

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["model_predict_completed"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        self._count += 1
        

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "3"
