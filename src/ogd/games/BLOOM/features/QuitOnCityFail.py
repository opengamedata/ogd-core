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
        return ["failure_event", "win_event", "city_alert", "policy_change"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        # Update failure type, county, city failure reason if a failure event is triggered
        if event.EventName == "failure_event":
            self.last_fail_type = event.GameState.get("fail_type", None)
            self.last_fail_county = event.GameState.get("fail_county", None)

            # If the failure was a city failure, capture city failure reason
            if self.last_fail_type == "CityFailed":
                self.city_failure_reason = event.GameState.get("city_failure_reason", None)

        # Update win status if a win event is triggered
        if event.EventName == "win_event":
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
