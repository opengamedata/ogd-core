from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.games.BLOOM.features.PerCountyFeature import PerCountyFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

class CountyPolicyChangeCount(PerCountyFeature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.policy_change_count: int = 0
        self.county_name: Optional[str] = None

    # Implement abstract functions
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["select_policy_card", "county_unlocked"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        event_type = event.EventName
        county_name = event.EventData.get("county_name", None)
        
        if event_type == "county_unlocked" and county_name:
            # If the county name matches the self.CountIndex, start tracking
            if county_name == self.params.CountIndex:
                self.county_name = county_name
        
        if event_type == "select_policy_card" and self.county_name:
            # Count the policy changes if the county is being tracked
            self.policy_change_count += 1

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self.policy_change_count]

    def Subfeatures(self) -> List[str]:
        return ["Count"]

    # Optionally override public functions
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
