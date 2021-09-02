from schemas import Event
import typing
from typing import Any, List, Union
# local imports
from extractors.Feature import Feature
from schemas.Event import Event

class SliderAverageRange(Feature):
    def __init__(self, name:str, description:str, count_index:int):
        Feature.__init__(self, name=name, description=description, count_index=count_index)
        self._ranges = []

    def GetEventTypes(self) -> List[str]:
        return ["CUSTOM.1"]
        # return ["SLIDER_MOVE_RELEASE"]

    def CalculateFinalValues(self) -> Any:
        return sum(self._ranges) / len(self._ranges)

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_data["level"] == self._count_index:
            self._ranges.append(event.event_data["max_val"] - event.event_data["min_val"])

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None
