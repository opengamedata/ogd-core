from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from ogd.games.BLOOM.features.PerCountyFeature import PerCountyFeature

class CountyFailCount(PerCountyFeature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.county_fail_counts: Dict[str, int] = {
            "Total": 0,
            "CityFailed": 0,
            "TooManyBlooms": 0,
            "OutOfMoney": 0
        }

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["lose_game"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        county_name = event.EventData.get("county_name", None)
        fail_type = event.EventData.get("lose_condition", "")

        if county_name:
            self.county_fail_counts["Total"] += 1

            if fail_type in self.county_fail_counts:
                self.county_fail_counts[fail_type] += 1

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        all_values = []
        all_values.extend([
            self.county_fail_counts.get("Total", "NOT RECORDED"),
            self.county_fail_counts.get("CityFailed", "NOT RECORDED"),
            self.county_fail_counts.get("TooManyBlooms", "NOT RECORDED"),
            self.county_fail_counts.get("OutOfMoney", "NOT RECORDED")
        ])
        return all_values

    def Subfeatures(self) -> List[str]:
        return ["CityFailed", "TooManyBlooms", "OutOfMoney"]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
