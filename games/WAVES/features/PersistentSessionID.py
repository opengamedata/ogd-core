from schemas import Event
from typing import Any, List, Union
# local imports
from features.SessionFeature import SessionFeature
from schemas.Event import Event

class PersistentSessionID(SessionFeature):
    def __init__(self, name:str, description:str):
        SessionFeature.__init__(self, name=name, description=description)
        self._persistent_id : Union[int,None] = None

    def GetEventTypes(self) -> List[str]:
        return ["BEGIN.0"]

    def GetFeatureValues(self) -> List[Any]:
        return [self._persistent_id]

    def _extractFromEvent(self, event:Event) -> None:
        if self._persistent_id is None:
            self._persistent_id = event.event_data['persistent_session_id']

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None


