# import libraries
import json
from typing import Any, List, Optional
# import local files
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData


class HouseBuildCount(Feature):
    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self.build_house_count = 0

    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.7"] 

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        buy_value = event.event_data.get("buy", None)
        if buy_value == 1:
            self.build_house_count += 1
            
    def _updateFromFeatureData(self, feature: FeatureData):
        pass

    def _getFeatureValues(self) -> List[Any]:
        return [self.build_house_count]
