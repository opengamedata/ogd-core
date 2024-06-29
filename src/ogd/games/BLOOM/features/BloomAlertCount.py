# import libraries
from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class BloomAlertCount(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.bloom_alert_counts: Dict[str, int] = {}

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["algae_growth_begin", "algae_growth_end"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        county_name = event.EventData.get("county_name", None)
        if county_name:
            if county_name not in self.bloom_alert_counts:
                self.bloom_alert_counts[county_name] = 1
            else:
                self.bloom_alert_counts[county_name] += 1

    def _updateFromFeatureData(self, feature: FeatureData):
        pass

    def _getFeatureValues(self) -> List[Any]:
        total_bloom_alert_count = sum(self.bloom_alert_counts.values())
        return [total_bloom_alert_count, self.bloom_alert_counts]

    def Subfeatures(self) -> List[str]:
        return ["Breakdown"]
