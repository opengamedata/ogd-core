# import libraries
from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

from ogd.games.BLOOM.features.PerCountyFeature import PerCountyFeature

class CountyBloomAlertCount(PerCountyFeature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.county_bloom_alert_counts: Dict[str, int] = {}
        self.focused_county: Optional[str] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["bloom_alert", "switch_county"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        if event.EventName == "switch_county":
            self.focused_county = event.GameState.get("current_county", None)
        elif event.EventName == "bloom_alert":
            county_name = event.GameState.get("current_county", None)
            if county_name:
                if county_name not in self.county_bloom_alert_counts:
                    self.county_bloom_alert_counts[county_name] = 1
                else:
                    self.county_bloom_alert_counts[county_name] += 1

    def _updateFromFeatureData(self, feature: FeatureData):
        pass

    def _getFeatureValues(self) -> List[Any]:
        if self.focused_county:
            return [self.county_bloom_alert_counts.get(self.focused_county, 0)]
        return [0]

    def Subfeatures(self) -> List[str]:
        return []

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
