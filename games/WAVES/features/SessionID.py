from schemas import Event
from typing import Any, List, Union
# local imports
from features.FeatureData import FeatureData
from features.SessionFeature import SessionFeature
from schemas.Event import Event

class SessionID(SessionFeature):
    def __init__(self, name:str, description:str, sessionID:str):
        SessionFeature.__init__(self, name=name, description=description)
        self._sessionID = sessionID

    def GetEventDependencies(self) -> List[str]:
        return []

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        return [self._sessionID]

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None

