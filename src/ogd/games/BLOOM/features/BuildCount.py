# import libraries
from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

class BuildCount(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.build_counts: Dict[str, int] = {}

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["click_execute_build"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        county_name = event.GameState.get("current_county", None)
        if county_name:
            if county_name not in self.build_counts:
                self.build_counts[county_name] = 1
            else:
                self.build_counts[county_name] += 1

    def _updateFromFeatureData(self, feature: FeatureData):
        pass

    def _getFeatureValues(self) -> List[Any]:
        total_build_count = sum(self.build_counts.values())
        return [total_build_count, self.build_counts]

    def Subfeatures(self) -> List[str]:
        return ["Breakdown"]