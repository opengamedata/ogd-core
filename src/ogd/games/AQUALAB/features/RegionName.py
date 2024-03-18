# import libraries
from typing import Any, List, Optional
# import locals
from ogd.core.extractors.Extractor import ExtractorParameters
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData
from ogd.core.extractors.features.PerCountFeature import PerCountFeature

class RegionName(PerCountFeature):
    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        regions = ['arctic', 'coral', 'bayou', 'kelp', 'other']
        self.count = 0
        self.region = regions[self.CountIndex]
    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _validateEventCountIndex(self, event:Event):
        pass

    def _extractFromEvent(self, event:Event) -> None:
        pass

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self.region]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
