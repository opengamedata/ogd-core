# import libraries
from schemas import Event
from typing import Any, List, Union
# import locals
from schemas.FeatureData import FeatureData
from features.SessionFeature import SessionFeature
from schemas.Event import Event

class OverallPercentAmplitudeMoves(SessionFeature):
    def __init__(self, name:str, description:str):
        SessionFeature.__init__(self, name=name, description=description)
        self._amplitude_count = 0
        self._move_count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["CUSTOM.1", "CUSTOM.2"]
        # return ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._move_count += 1
        if event.event_data["slider"].upper() == "AMPLITUDE":
            self._amplitude_count += 1

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if self._move_count > 0:
            return [self._amplitude_count / self._move_count * 100]
        else:
            return [None]

    # *** Optionally override public functions. ***
