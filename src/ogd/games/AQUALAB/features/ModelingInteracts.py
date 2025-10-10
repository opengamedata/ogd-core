# import libraries
from datetime import datetime, timedelta
import logging, warnings
from typing import Any, List, Optional
from ogd.games.AQUALAB.features.PerJobFeature import PerJobFeature
# import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature


class ModelingInteracts(PerJobFeature):

    def __init__(self, params:GeneratorParameters, job_map:dict):
        self._job_map = job_map
        super().__init__(params=params, job_map=job_map)
        self._begin = False
        self._count = 0 
        
        

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["begin_model", "model_intervene_error", "model_intervene_update", "model_predict_completed", "simulation_sync_achieved", "model_concept_exported", "model_concept_started","model_ecosystem_selected", "model_phase_changed"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        self._count += 1
        


        

    def _updateFromFeaturef, feature:FeatFeature
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return 
