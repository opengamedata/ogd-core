# import libraries
import logging
from typing import Any, List, Optional
# import locals
from utils.Logger import Logger
from extractors.Extractor import ExtractorParameters
from games.AQUALAB.features.PerJobFeature import PerJobFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData

class JobExperimentInteracts(PerJobFeature):

    def __init__(self, params:ExtractorParameters, job_map:dict):
        super().__init__(params=params, job_map=job_map)
        self._active = False
        self._count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["add_environment", "remove_environment", "add_critter", "remove_critter", "receive_fact", "begin_experiment", "end_experiment"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if(event.EventName == "begin_experiment"):
            self._active = True
        if(event.EventName == "end_experiment"):
            self.active = False
        
        if(event.EventName == "receive_fact"):
            if(self._active == True):#only count receive_fact if it is during the experiment stage here
                self._count += 1
        else:
            self._count += 1


    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return
