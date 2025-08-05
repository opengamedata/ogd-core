from collections import Counter
from typing import Any, List, Optional

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature

class AlertCount(Extractor):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.alert_counts: Counter = Counter()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["local_alert_displayed"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        alert_type = event.EventData.get("alert_type", "").upper()
        if alert_type != "GLOBAL":
            self.alert_counts[alert_type] += 1

    def _updateFromFeature(self, feature: Feature):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [
            sum(self.alert_counts.values()),
            self.alert_counts["DIALOGUE"],
            self.alert_counts["CRITIMBALANCE"],
            self.alert_counts["DIEOFF"],
            self.alert_counts["DECLININGPOP"],
            self.alert_counts["EXCESSRUNOFF"],
            self.alert_counts["SELLINGLOSS"],
        ]

    def Subfeatures(self) -> List[str]:
        return ["Dialogue", "CritImbalance", "DieOff", "DecliningPop", "ExcessRunoff", "SellingLoss"]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
