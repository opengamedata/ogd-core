from schemas import Event
import typing
from typing import Any, List, Union
# local imports
from extractors.SessionFeature import SessionFeature
from schemas.Event import Event

class AverageSliderMoves(SessionFeature):
    def __init__(self, name:str, description:str):
        SessionFeature.__init__(self, name=name, description=description)
        self._levels_encountered : set = set()
        self._slider_count       : int = 0

    def GetEventTypes(self) -> List[str]:
        return ["CUSTOM.1"]
        # return ["SLIDER_MOVE_RELEASE"]

    def GetFeatureValues(self) -> List[Any]:
        if len(self._levels_encountered) > 0:
            return self._slider_count / len(self._levels_encountered)
        else:
            return None

    def _extractFromEvent(self, event:Event) -> None:
        self._levels_encountered.add(event.event_data['level']) # set-add level to list, at end we will have set of all levels seen.
        self._slider_count += 1

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None


