# import libraries
from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature

from ogd.core.generators.extractors.Extractor import Extractor

class QuitOnBloomFail(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.last_fail_type: Optional[str] = None
        self.won: Optional[bool] = None
        self.last_fail_county: Optional[str] = None
        self.bloom_count: int = 0
        self.skim_policy: Optional[str] = None
        self.runoff_policy: Optional[str] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        # Using actual event names based on BLOOM.json.template
        return ["lose_game", "win_game", "bloom_alert", "select_policy_card"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        # Update failure type, county, bloom count, and policies if a lose event is triggered
        match event.EventName:
            case "bloom_alert":
                self.bloom_count += 1
            case "lose_game":
                self.last_fail_type = event.EventData.get("lose_condition", None)
                self.last_fail_county = event.EventData.get("county_name", None)

                # If the failure was due to bloom (too many blooms), capture bloom count and policies
                if self.last_fail_type == "TooManyBlooms":
                    self.skim_policy = event.GameState.get("county_policies", {}).get("cleanup", {}).get("policy_choice", None)
                    self.runoff_policy = event.GameState.get("county_policies", {}).get("runoff", {}).get("policy_choice", None)
            # Update win status if a win event is triggered
            case "win_game":
                self.won = True
            case _:
                self.won = False

    def _updateFromFeatureData(self, feature: FeatureData):
        pass

    def _getFeatureValues(self) -> List[Any]:
        # Check if the player lost and the last failure type was "TooManyBlooms"
        if self.last_fail_type == "TooManyBlooms" and not self.won:
            return [1, self.last_fail_county, self.bloom_count, self.skim_policy, self.runoff_policy]
        else:
            # Return default values if the condition isn't met
            return [0, None, None, None, None]

    def Subfeatures(self) -> List[str]:
        # Subfeatures are: last_fail_county, bloom_count, skim_policy, runoff_policy
        return ["FailureCounty", "BloomCount", "SkimPolicy", "RunoffPolicy"]
