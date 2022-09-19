# import libraries
from typing import Any, List
# import locals
from extractors.features.Feature import Feature
from extractors.Extractor import ExtractorParameters
from schemas.FeatureData import FeatureData
from schemas.Event import Event

class MoveShapeCount(Feature):
    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["move_shape"]

    @classmethod
    _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._count += 1

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***
