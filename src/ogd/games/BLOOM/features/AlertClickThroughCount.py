from collections import Counter
from datetime import timedelta
from typing import Any, Dict, List, Optional

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

class AlertClickThrough(Feature):
    DEFAULT_READING_RATE = 200*2
    def __init__(self, params: GeneratorParameters, max_reading_rate:int=DEFAULT_READING_RATE):
        """Feature to estimate when players 

        :param params: _description_
        :type params: GeneratorParameters
        :param max_reading_rate: The rate, in words per minute, at which the fastest "real" readers are assumed to read.
            Players who "read" at more than the max reading rate are treated as click-throughs.
            defaults to DEFAULT_READING_RATE of 400 (twice the average estimated reading rate of 200 WPM from https://www.prsa.org/article/how-to-determine-average-reading-time)
        :type max_reading_rate: int, optional
        """
        super().__init__(params=params)
        self._max_rate = max_reading_rate
        self._in_dialog = False
        self._current_read_rates: List[float] = []
        self._last_line : Optional[str] = None
        self._clickthrough_count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["click_local_alert", "dialogue_start", "dialogue_end", "click_next_character_line", "character_line_displayed"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        match event.EventName:
            case "click_local_alert":
                if len(self._current_read_rates) > 0:
                    _avg = sum(self._current_read_times, timedelta(0)) / len(self._current_read_times)
                    self._clickthrough_count += 1 if _avg 

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
