from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class AlertCount(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.alert_counts: Dict[str, int] = {
            "DieOff": 0,
            "DecliningPop": 0,
            "SellingLoss": 0,
            "CritImbalance": 0
        }

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["local_alert_displayed"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        alert_type = event.EventData.get("alert_type", "")
        if alert_type in self.alert_counts:
            self.alert_counts[alert_type] += 1

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [
            sum(self.alert_counts.values()),
            self.alert_counts["DieOff"],
            self.alert_counts["DecliningPop"],
            self.alert_counts["SellingLoss"],
            self.alert_counts["CritImbalance"]
        ]

    def Subfeatures(self) -> List[str]:
        return ["DieOff", "DecliningPop", "SellingLoss", "CritImbalance"]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
