from typing import Any, List

from features.FeatureData import FeatureData
from features.SessionFeature import SessionFeature
from schemas.Event import Event

class EchoSessionID(SessionFeature):

    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description)

    def GetEventDependencies(self) -> List[str]:
        return []

    def GetFeatureDependencies(self) -> List[str]:
        return ["SessionID"]

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        self._session_id = feature.FeatureValues()[0]

    def GetFeatureValues(self) -> List[Any]:
        return [f"The sess ID is: {self._session_id}"]
