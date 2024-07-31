# import libraries
from ogd.core.models import Event
import typing
from typing import Any, List, Optional
# import locals
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class TimeToAnswerMS(Feature):
    def __init__(self, params:GeneratorParameters):
        Feature.__init__(self, params=params)
        self._latest_complete_lvl8  = None
        self._latest_complete_lvl16 = None
        self._latest_answer_Q0 = None
        self._latest_answer_Q2 = None
        self._answer_time = None

    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.3", "COMPLETE.0"]
        # return ["QUESTION_ANSWER"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if event.EventName == "COMPLETE.0":
            if event.GameState['level'] == 8:
                self._latest_complete_lvl8 = event.Timestamp
            if event.GameState['level'] == 16:
                self._latest_complete_lvl16 = event.Timestamp
        elif event.EventName == "CUSTOM.3":
            q_num = event.EventData["question"]
            if (q_num == 0):
                self._latest_answer_Q0 = event.Timestamp
            elif (q_num == 2):
                self._latest_answer_Q2 = event.Timestamp
            if self.CountIndex == q_num:
                self._answer_time = self._calcAnswerTime(timestamp=event.Timestamp)

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return ["Not Implemented"]

    # *** Optionally override public functions. ***

    # *** Other local functions
    def _calcAnswerTime(self, timestamp) -> Optional[int]:
        millis: Optional[float]
        if self.CountIndex == 0:
            millis = 1000.0 * (timestamp - self._latest_complete_lvl8).total_seconds()
        elif self.CountIndex == 1:
            millis = 1000.0 * (timestamp - self._latest_answer_Q0).total_seconds()
        elif self.CountIndex == 2:
            millis = 1000.0 * (timestamp - self._latest_complete_lvl16).total_seconds()
        elif self.CountIndex == 3:
            millis = 1000.0 * (timestamp - self._latest_answer_Q2).total_seconds()
        else:
            millis = None
        return int(millis) if millis is not None else None