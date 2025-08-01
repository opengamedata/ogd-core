# import libraries
import json
from typing import Any, List, Optional
# import local files
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature


class TotalBuildCount(Extractor):
    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self.total_build_count = 0

    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.7"] 

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        buy_value = event.event_data.get("buy", None)
        if buy_value in [1,3,5]:
            self.total_build_count += 1
            
    def _updateFromFeatureData(self, feature: FeatureData):
        pass

    def _getFeatureValues(self) -> List[Any]:
        return [self.total_build_count]

