from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class CountyFailCount(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.county_fail_counts: Dict[str, Dict[str, int]] = {}

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
            if county_name not in self.county_fail_counts:
                self.county_fail_counts[county_name] = {
                    "Total": 0,
                    "CityFailed": 0,
                    "TooManyBlooms": 0,
                    "OutOfMoney": 0
                }

            self.county_fail_counts[county_name]["Total"] += 1

            if fail_type in self.county_fail_counts[county_name]:
                self.county_fail_counts[county_name][fail_type] += 1

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        all_values = []
        for county_name, fail_counts in self.county_fail_counts.items():
            all_values.extend([
                fail_counts["Total"],
                fail_counts["CityFailed"],
                fail_counts["TooManyBlooms"],
                fail_counts["OutOfMoney"]
            ])
        return all_values

    def Subfeatures(self) -> List[str]:
        return ["CityFailed", "TooManyBlooms", "OutOfMoney"]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
