# import libraries
from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

# import PerCountyFeature
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.games.BLOOM.features.PerCountyFeature import PerCountyFeature

class FailureTrackingFeature(PerCountyFeature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.last_fail_type: Optional[str] = None
        self.won: Optional[bool] = None
        self.last_fail_county: Optional[str] = None
        self.bloom_count: Optional[int] = None
        self.skim_policy: Optional[str] = None
        self.runoff_policy: Optional[str] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["failure_event", "win_event", "bloom_alert", "policy_change"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        # Update failure type, county, bloom count, policies if a failure event is triggered
        if event.EventName == "failure_event":
            self.last_fail_type = event.GameState.get("fail_type", None)
            self.last_fail_county = event.GameState.get("fail_county", None)

            # If the failure was a bloom failure, capture bloom count and policies
            if self.last_fail_type == "TooManyBlooms":
                self.bloom_count = event.GameState.get("bloom_count", None)
                self.skim_policy = event.GameState.get("skim_policy", None)
                self.runoff_policy = event.GameState.get("runoff_policy", None)

        # Update win status if a win event is triggered
        if event.EventName == "win_event":
            self.won = True
        else:
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
