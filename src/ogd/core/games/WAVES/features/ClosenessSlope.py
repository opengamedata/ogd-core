# import libraries
from schemas import Event
from typing import Any, List, Optional
# import locals
from extractors.features.Feature import Feature
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData


class ClosenessSlope(Feature):
    def __init__(self, params:ExtractorParameters):
        Feature.__init__(self, params=params)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return ["Not Implemented"]

    # *** Optionally override public functions. ***
