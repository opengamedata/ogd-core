# import libraries
from typing import Any, List
# import locals
from features.FeatureData import FeatureData
from features.SessionFeature import SessionFeature
from schemas.Event import Event

class EchoSessionID(SessionFeature):

    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return []

    def _getFeatureDependencies(self) -> List[str]:
        return ["SessionID"]

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        self._session_id = feature.FeatureValues()[0]

    def _getFeatureValues(self) -> List[Any]:
        return [f"The sess ID is: {self._session_id}"]

    # *** Optionally override public functions. ***
