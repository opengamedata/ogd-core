# import libraries
import logging
from typing import Any, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.Extractor import ExtractorParameters
from ogd.games.AQUALAB.features.PerJobFeature import PerJobFeature
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData

class JobDiveSitesCount(PerJobFeature):
    def __init__(self, params:ExtractorParameters, job_map:dict):
        super().__init__(params=params, job_map=job_map)
        self._count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["begin_dive"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
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
