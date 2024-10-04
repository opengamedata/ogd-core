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
        return ["select_policy_card"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        if event.EventName == "select_policy_card":
            # Count the policy changes if the county is being tracked
            self.policy_change_count += 1

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self.policy_change_count]

    # Optionally override public functions
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
