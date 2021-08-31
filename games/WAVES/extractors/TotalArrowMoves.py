from schemas import Event
import typing
from typing import Any, List, Union
# local imports
from extractors.Feature import Feature
from schemas.Event import Event

class TotalArrowMoves(Feature):
    def __init__(self, name:str, description:str, count_index:int):
        Feature.__init__(self, name=name, description=description, count_index=count_index)

    def GetEventTypes(self) -> List[str]:
        return []

    def CalculateFinalValues(self) -> Any:
        return

    def _extractFromEvent(self, event:Event) -> None:
        return

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None
