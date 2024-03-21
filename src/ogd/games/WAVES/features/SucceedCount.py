# import libraries
import typing
from typing import Any, List, Optional
# import locals
from ogd.core.generators.extractors.PerLevelFeature import PerLevelFeature
from ogd.core.generators.Extractor import ExtractorParameters
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData

class SucceedCount(PerLevelFeature):
    def __init__(self, params:ExtractorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._succeed_count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["SUCCEED.0"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._succeed_count += 1

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._succeed_count]

    # *** Optionally override public functions. ***
