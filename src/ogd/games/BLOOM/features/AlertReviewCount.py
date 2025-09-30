from collections import Counter
from typing import Any, List, Optional

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

class AlertReviewCount(Feature):
    """Feature to indicate how often players "reviewed" an alert.

    Here, "review" refers to a case where a player opened an alert,
    as opposed to a "response" in which they took some additional action based on the alert.
    """
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.alert_review_counts: Counter = Counter()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["click_local_alert"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        alert_type = event.EventData.get("alert_type", "").upper()
        if alert_type != "GLOBAL":
            self.alert_review_counts[alert_type] += 1

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [
            sum(self.alert_review_counts.values()),
            self.alert_review_counts["DIALOGUE"],
            self.alert_review_counts["CRITIMBALANCE"],
            self.alert_review_counts["DIEOFF"],
            self.alert_review_counts["DECLININGPOP"],
            self.alert_review_counts["EXCESSRUNOFF"],
            self.alert_review_counts["SELLINGLOSS"],
        ]

    def Subfeatures(self) -> List[str]:
        return ["Dialogue", "CritImbalance", "DieOff", "DecliningPop", "ExcessRunoff", "SellingLoss"]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
