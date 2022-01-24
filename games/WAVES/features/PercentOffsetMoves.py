from schemas import Event
from typing import Any, List, Union
# local imports
from features.Feature import Feature
from schemas.Event import Event

class PercentOffsetMoves(Feature):
    def __init__(self, name:str, description:str, count_index:int):
        Feature.__init__(self, name=name, description=description, count_index=count_index)
        self._offset_count = 0
        self._count = 0

    def GetEventTypes(self) -> List[str]:
        return ["CUSTOM.1", "CUSTOM.2"]
        # return ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"]

    def GetFeatureValues(self) -> List[Any]:
        return [self._offset_count / self._count if self._count != 0 else None]

    def _extractFromEvent(self, event:Event) -> None:
        self._count += 1
        if event.event_data['slider'].upper() == 'OFFSET':
            self._offset_count += 1

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None
