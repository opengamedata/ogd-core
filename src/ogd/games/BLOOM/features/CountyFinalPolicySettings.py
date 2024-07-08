# import libraries
from typing import Any, Dict, List
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class CountyFinalPolicySettings(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.policy_settings: Dict[str, Dict[str, str]] = {
            "Hillsaide": {},
            "Forest": {},
            "Prairie": {},
            "Wetland": {},
            "Urban": {}
        }
        for county in self.policy_settings.keys():
            self.policy_settings[county] = {"policy1": None, "policy2": None, "policy3": None}

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["select_policy_card"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        county_name = event.EventData.get("county_name", None)
        policy_name = event.EventData.get("policy", None)
        choice_name = event.EventData.get("choice_name", None)

        if county_name and policy_name and choice_name is not None:
            if county_name in self.policy_settings:
                self.policy_settings[county_name][policy_name] = choice_name

    def _updateFromFeatureData(self, feature: FeatureData):
        pass

    def _getFeatureValues(self) -> List[Any]:
        return [self.policy_settings]

    def Subfeatures(self) -> List[str]:
        return []
