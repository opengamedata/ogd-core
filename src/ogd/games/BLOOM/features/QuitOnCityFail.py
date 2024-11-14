# import libraries
from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

# import PerCountyFeature
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.games.BLOOM.features.PerCountyFeature import PerCountyFeature

class QuitOnCityFail(PerCountyFeature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.last_fail_type: Optional[str] = None
        self.won: Optional[bool] = None
        self.last_fail_county: Optional[str] = None
        self.city_failure_reason: Optional[str] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        # Using actual event names based on BLOOM.json.template
        return ["lose_game", "win_game", "local_alert_displayed", "select_policy_card"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        # Update failure type, county, and reason if a lose event is triggered
        if event.EventName == "lose_game":
            self.last_fail_type = event.EventData.get("lose_condition", None)
            self.last_fail_county = event.GameState.get("current_county", None)

            # If the failure was a city failure, capture city failure reason
            if self.last_fail_type == "CityFailed":
                self.city_failure_reason = "Population Decline"  # Assuming a general reason, as no specific key is available

        # Update win status if a win event is triggered
        elif event.EventName == "win_game":
            self.won = True
        else:
            self.won = False

    def _updateFromFeatureData(self, feature: FeatureData):
        pass

    def _getFeatureValues(self) -> List[Any]:
        # Check if the player lost and the last failure type was "CityFailed"
        if self.last_fail_type == "CityFailed" and not self.won:
            return [1, self.last_fail_county, self.city_failure_reason]
        else:
            # Return default values if the condition isn't met
            return [0, None, None]

    def Subfeatures(self) -> List[str]:
        # Subfeatures are: last_fail_county, city_failure_reason
        return ["FailureCounty", "CityFailureReason"]
