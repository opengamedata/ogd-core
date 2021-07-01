from schemas import Event
import typing
from typing import Any, List
# local imports
from extractors.Feature import Feature
from schemas.Event import Event

class PercentOffsetMoves(Feature):
    def __init__(self, name:str, description:str, sessionID:str):
        min_version = None
        max_version = None
        Feature.__init__(self, name=name, description=description, min_version=min_version, max_version=max_version)
        self._sessionID = sessionID

    def GetEventTypes(self) -> List[str]:
        return []

    def CalculateFinalValues(self) -> Any:
        return self._sessionID

    def _extractFromEvent(self, event:Event) -> None:
        return

