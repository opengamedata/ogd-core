# import libraries
from schemas import Event
import typing
from typing import Any, List, Union
# import locals
from schemas.FeatureData import FeatureData
from features.Feature import Feature
from schemas.Event import Event

class TimeToAnswerMS(Feature):
    def __init__(self, name:str, description:str, count_index:int):
        Feature.__init__(self, name=name, description=description, count_index=count_index)
        self._latest_complete_lvl8  = None
        self._latest_complete_lvl16 = None
        self._latest_answer_Q0 = None
        self._latest_answer_Q2 = None
        self._answer_time = None

    def _getEventDependencies(self) -> List[str]:
        return ["CUSTOM.3", "COMPLETE.0"]
        # return ["QUESTION_ANSWER"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_name == "COMPLETE.0":
            if event.event_data['level'] == 8:
                self._latest_complete_lvl8 = event.timestamp
            if event.event_data['level'] == 16:
                self._latest_complete_lvl16 = event.timestamp
        elif event.event_name == "CUSTOM.3":
            q_num = event.event_data["question"]
            if (q_num == 0):
                self._latest_answer_Q0 = event.timestamp
            elif (q_num == 2):
                self._latest_answer_Q2 = event.timestamp
            if self._count_index == q_num:
                self._answer_time = self._calcAnswerTime(timestamp=event.timestamp)

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return ["Not Implemented"]

    # *** Optionally override public functions. ***

    # *** Other local functions
    def _calcAnswerTime(self, timestamp) -> Union[int,None]:
        millis: Union[float,None]
        if self._count_index == 0:
            millis = 1000.0 * (timestamp - self._latest_complete_lvl8).total_seconds()
        elif self._count_index == 1:
            millis = 1000.0 * (timestamp - self._latest_answer_Q0).total_seconds()
        elif self._count_index == 2:
            millis = 1000.0 * (timestamp - self._latest_complete_lvl16).total_seconds()
        elif self._count_index == 3:
            millis = 1000.0 * (timestamp - self._latest_answer_Q2).total_seconds()
        else:
            millis = None
        return int(millis) if millis is not None else None