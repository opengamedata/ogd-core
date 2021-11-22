from schemas import Event
from typing import Any, List, Union
# local imports
from extractors.PerLevelFeature import PerLevelFeature
from schemas.Event import Event

class TotalSliderMoves(PerLevelFeature):
    def __init__(self, name:str, description:str, count_index:int):
        PerLevelFeature.__init__(self, name=name, description=description, count_index=count_index)
        self._slider_move_count : int = 0

    def GetEventTypes(self) -> List[str]:
        return ["CUSTOM.1"]
        # return ["SLIDER_MOVE_RELEASE"]

    def GetFeatureValues(self) -> List[Any]:
        return [self._slider_move_count]

    def _extractFromEvent(self, event:Event) -> None:
            self._slider_move_count += 1

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None
