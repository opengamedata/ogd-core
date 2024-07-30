# import necessary libraries
from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class FailCount(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.fail_counts: Dict[str, int] = {
            "CityFailed": 0,
            "TooManyBlooms": 0,
            "OutOfMoney": 0
        }

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["lose_game"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        lose_condition = event.EventData.get("lose_condition", "")
        if lose_condition:
            if lose_condition in self.fail_counts:
                self.fail_counts[lose_condition] += 1

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        _total = sum([val for val in self.fail_counts.values()])
        return [_total, self.fail_counts]

    def Subfeatures(self) -> List[str]:
        return ["Breakdown"]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
