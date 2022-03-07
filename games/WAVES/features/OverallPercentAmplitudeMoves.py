from schemas import Event
from typing import Any, List, Union
# local imports
from features.FeatureData import FeatureData
from features.SessionFeature import SessionFeature
from schemas.Event import Event

class OverallPercentAmplitudeMoves(SessionFeature):
    def __init__(self, name:str, description:str):
        SessionFeature.__init__(self, name=name, description=description)
        self._amplitude_count = 0
        self._move_count = 0

    def GetEventDependencies(self) -> List[str]:
        return ["CUSTOM.1", "CUSTOM.2"]
        # return ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        if self._move_count > 0:
            return [self._amplitude_count / self._move_count * 100]
        else:
            return [None]

    def _extractFromEvent(self, event:Event) -> None:
        self._move_count += 1
        if event.event_data["slider"].upper() == "AMPLITUDE":
            self._amplitude_count += 1

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None
