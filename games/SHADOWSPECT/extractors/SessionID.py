from typing import Any, List

from extractors.SessionFeature import SessionFeature
from schemas.Event import Event

class SessionID(SessionFeature):
    def __init__(self, name:str, description:str, session_id:str):
        self._session_id = session_id
        super().__init__(name=name, description=description)

    def GetEventTypes(self) -> List[str]:
        return []

    def CalculateFinalValues(self) -> Any:
        return self._session_id

    def _extractFromEvent(self, event:Event) -> None:
        return
