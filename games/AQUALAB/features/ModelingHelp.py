# import libraries
from datetime import datetime, timedelta
import logging, warnings
from typing import Any, List, Optional
from games.AQUALAB.features.PerJobFeature import PerJobFeature
# import locals
from utils.Logger import Logger
from extractors.Extractor import ExtractorParameters
from extractors.features.Feature import Feature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData


class ModelingHelp(PerJobFeature):

    def __init__(self, params:ExtractorParameters, job_map:dict):
        self._job_map = job_map
        super().__init__(params=params, job_map=job_map)
        self._found = False
        self._help = False
        

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["ask_for_help", "begin_model"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if(event.EventName == "begin_model"):
            self._found = True
        if(self._found == True and event.EventName == "ask_for_help"):
            self._help = True

        

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if(self._help == True):
            return [1]
        else:
            return [0]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return 
