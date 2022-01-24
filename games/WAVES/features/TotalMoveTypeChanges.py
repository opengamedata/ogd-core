from schemas import Event
import typing
from typing import Any, List, Union
# local imports
from features.PerLevelFeature import PerLevelFeature
from schemas.Event import Event

class TotalMoveTypeChanges(PerLevelFeature):
    def __init__(self, name:str, description:str, count_index:int):
        PerLevelFeature.__init__(self, name=name, description=description, count_index=count_index)
        self._last_move = None
        self._change_count = 0

    def GetEventTypes(self) -> List[str]:
        return ["CUSTOM.1", "CUSTOM.2"]
        # return ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"]

    def GetFeatureValues(self) -> List[Any]:
        return [self._change_count]

    def _extractFromEvent(self, event:Event) -> None:
        if self._last_move != event.event_name:
            self._change_count += 1
        self._last_move = event.event_name

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None
