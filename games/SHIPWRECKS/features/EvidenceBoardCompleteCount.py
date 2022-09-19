# import libraries
from typing import Any, List, Optional
# import locals
from schemas.FeatureData import FeatureData
from extractors.features.Feature import Feature
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event

class EvidenceBoardCompleteCount(Feature):

    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["evidence_board_complete"]

    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._count += 1

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***