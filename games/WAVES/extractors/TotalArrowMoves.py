from schemas import Event
from typing import Any, List, Union
# local imports
from extractors.Feature import Feature
from schemas.Event import Event

class TotalArrowMoves(Feature):
    def __init__(self, name:str, description:str, count_index:int):
        Feature.__init__(self, name=name, description=description, count_index=count_index)
        self._arrow_move_count : int = 0

    def GetEventTypes(self) -> List[str]:
        return ["CUSTOM.2"]
        # return ["ARROW_MOVE_RELEASE"]

    def CalculateFinalValues(self) -> Any:
        return self._arrow_move_count

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_data["level"] == self._count_index and event.event_name == "ARROW_MOVE_RELEASE":
            self._arrow_move_count += 1

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None
