# import libraries
import logging
from typing import Any, List, Optional
# import locals
from utils import Logger
from extractors.Extractor import ExtractorParameters
from games.AQUALAB.features.PerJobFeature import PerJobFeature
from schemas.Event import Event
from schemas.FeatureData import FeatureData

class JobHelpCount(PerJobFeature):

    def __init__(self, params:ExtractorParameters, job_map:dict):
        self._job_map = job_map
        super().__init__(params=params, job_map=job_map)
        self._count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["ask_for_help"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._count += 1

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
