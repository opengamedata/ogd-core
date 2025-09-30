# import libraries
from datetime import datetime, timedelta
import logging, warnings
from typing import Any, List, Optional
from games.AQUALAB.features.PerDifficultyFeature import PerDifficultyFeature
# import locals
from utils.Logger import Logger
from extractors.Extractor import ExtractorParameters
from extractors.features.Feature import Feature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData


class ModelingInteractsPerDifficulty(PerDifficultyFeature):

    def __init__(self, params:ExtractorParameters, diff_map:dict, difficulty_type:Optional[str]):
        super().__init__(params=params, diff_map=diff_map, difficulty_type=difficulty_type)
        self._begin = False
        self._count = 0 
        
        

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["begin_model", "model_intervene_error", "model_intervene_update", "model_predict_completed", "simulation_sync_achieved", "model_concept_exported", "model_concept_started","model_ecosystem_selected", "model_phase_changed"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if(event.EventName == "begin_model"):
            self._begin = True
        if(self._begin == True):
            self._count += 1


        

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "3"
