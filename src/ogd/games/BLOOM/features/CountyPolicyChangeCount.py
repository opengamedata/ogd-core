from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.games.BLOOM.features.PerCountyFeature import PerCountyFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature

class CountyPolicyChangeCount(PerCountyFeature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.policy_change_count: int = 0
        self.policy_counts: Dict[str, int] = {
            "SalesTaxPolicy": 0,
            "RunoffPolicy": 0,
            "ImportTaxPolicy": 0,
            "SkimmingPolicy": 0
        }
        self.county_name: Optional[str] = None

    # Implement abstract functions
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["select_policy_card"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        if event.EventName == "select_policy_card":
            policy_name = event.EventData.get("policy", None)
            if policy_name in self.policy_counts:
                # Increment the specific policy count and the total count
                self.policy_counts[policy_name] += 1
                self.policy_change_count += 1
            else:
                self.WarningMessage(f"Got a select_policy_card with unexpected policy type {policy_name}")

    def _updateFromFeature(self, feature: Feature):
        pass

    def _getFeatureValues(self) -> List[Any]:
        # Return total count and individual policy counts
        return [
            self.policy_change_count,
            self.policy_counts["SalesTaxPolicy"],
            self.policy_counts["RunoffPolicy"],
            self.policy_counts["ImportTaxPolicy"],
            self.policy_counts["SkimmingPolicy"]
        ]

    def Subfeatures(self) -> List[str]:
        # List each individual policy count as a subfeature
        return [
            "SalesTaxPolicyCount",
            "RunoffPolicyCount",
            "ImportTaxPolicyCount",
            "SkimmingPolicyCount"
        ]

    # Optionally override public functions
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
