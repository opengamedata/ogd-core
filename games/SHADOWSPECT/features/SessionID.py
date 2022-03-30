# global imports
from typing import Any, List
# local imports
from features.SessionFeature import SessionFeature
from features.FeatureData import FeatureData
from schemas.Event import Event

class SessionID(SessionFeature):
    def __init__(self, name:str, description:str, session_id:str):
        self._session_id = session_id
        super().__init__(name=name, description=description)

    # *** Implement abstract functions ***
    def _getEventDependencies(self) -> List[str]:
        return []

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._session_id]

    # *** Optionally override public functions. ***
