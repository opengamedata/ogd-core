# import libraries
from typing import Any, List, Optional
# import locals
from ogd.core.generators.extractors.Extractor import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature

class RegionName(PerCountFeature):
    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        regions = ['arctic', 'coral', 'bayou', 'kelp', 'other']
        self.count = 0
        self.region = regions[self.CountIndex]
    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _validateEventCountIndex(self, event:Event):
        pass

    def _updateFromEvent(self, event:Event) -> None:
        pass

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self.region]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
