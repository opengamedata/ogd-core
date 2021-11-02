from schemas import Event
import typing
from typing import Any, List, Union
# local imports
from extractors.Feature import Feature
from schemas.Event import Event

class PercentOffsetGoodMoves(Feature):
    def __init__(self, name:str, description:str, count_index:int):
        Feature.__init__(self, name=name, description=description, count_index=count_index)
        self._offset_count = 0
        self._good_count = 0

    def GetEventTypes(self) -> List[str]:
        return ["CUSTOM.1", "CUSTOM.2"]
        # return ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"]

    def CalculateFinalValues(self) -> Any:
        return self._good_count / self._offset_count

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_data['slider'].upper() == 'OFFSET':
            self._offset_count += 1
            if event.event_data['closeness_end'] > event.event_data['closeness_start']:
                self._good_count += 1

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None
