from schemas import Event
import typing
from typing import Any, List, Optional
# import locals
from schemas.FeatureData import FeatureData
from extractors.features.PerLevelFeature import PerLevelFeature
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event

class TotalFails(PerLevelFeature):
    def __init__(self, params:ExtractorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._fail_count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
def _getEventDependencies(cls, mode:ExportMode) -> List[str]:
        return ["FAIL.0"]

    @classmethod
def _getEventDependencies(cls, mode:ExportMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._fail_count += 1

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._fail_count]

    # *** Optionally override public functions. ***
