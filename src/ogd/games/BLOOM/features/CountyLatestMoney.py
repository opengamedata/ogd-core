# import libraries
from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

# import PerCountyFeature
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.games.BLOOM.features.PerCountyFeature import PerCountyFeature

class CountyLatestMoney(PerCountyFeature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.latest_money: Optional[int] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["all_events"]
        # return ["switch_county"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        current_money = event.GameState.get("current_money", None)
        self.latest_money = current_money

    def _updateFromFeatureData(self, feature: FeatureData):
        pass

    def _getFeatureValues(self) -> List[Any]:
        return [self.latest_money]

    def Subfeatures(self) -> List[str]:
        return []
