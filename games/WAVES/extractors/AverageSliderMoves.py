from schemas import Event
import typing
from typing import Any, List, Union
# local imports
from extractors.SessionFeature import SessionFeature
from schemas.Event import Event

class AverageSliderMoves(SessionFeature):
    def __init__(self, name:str, description:str):
        SessionFeature.__init__(self, name=name, description=description)

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


