# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from utils.Logger import Logger
from extractors.Extractor import ExtractorParameters
from extractors.features.PerCountFeature import PerCountFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData

class JobPriorAttempt(PerCountFeature):

    def __init__(self, params:ExtractorParameters, job_map:dict):
        self._job_map = job_map
        super().__init__(params=params)
        self._prior_list = set()
        self._completed = False
        self._session_id : Optional[int] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["complete_job", "accept_job"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        job_data = event.EventData["job_name"]['string_value']
        if event.event_name == "complete_job":
            if self._job_map[job_data] == self.CountIndex:
                self._completed = True
                return
        else:
            if self._job_map[job_data] != self.CountIndex:
                self._prior_list.add(self._job_map[job_data])
                return

    def _validateEventCountIndex(self, event:Event) -> bool:
        return not self._completed

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [sorted(self._prior_list)]

    # *** Optionally override public functions. ***

    def Subfeatures(self) -> List[str]:
        return []

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
