# import libraries
from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from ogd.games.BLOOM.features.PerCountyFeature import PerCountyFeature

class CountyFinalPolicySettings(PerCountyFeature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.policy_settings: Dict[str, Optional[str]] = {
            "SalesTaxPolicy": None,
            "RunoffPolicy": None,
            "ImportTaxPolicy": None,
            "SkimmingPolicy": None
        }

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["select_policy_card"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        policy_name = event.EventData.get("policy", None)
        choice_name = event.EventData.get("choice_name", None)

        if policy_name is not None and choice_name is not None:
            if policy_name in self.policy_settings:
                self.policy_settings[policy_name] = choice_name
            else:
                self.WarningMessage(f"Got a select_policy_card with unexpected policy type {policy_name}")

    def _updateFromFeatureData(self, feature: FeatureData):
        pass

    def _getFeatureValues(self) -> List[Any]:
        # Return dictionary plus individual subfeatures
        return [
            self.policy_settings,
            self.policy_settings["SalesTaxPolicy"],
            self.policy_settings["RunoffPolicy"],
            self.policy_settings["ImportTaxPolicy"],
            self.policy_settings["SkimmingPolicy"]
        ]

    def Subfeatures(self) -> List[str]:
        # List each individual policy setting as a subfeature
        return [
            "SalesTaxPolicy",
            "RunoffPolicy",
            "ImportTaxPolicy",
            "SkimmingPolicy"
        ]
