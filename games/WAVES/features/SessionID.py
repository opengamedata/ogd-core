# import libraries
from schemas import Event
from typing import Any, List, Optional
# import locals
from schemas.FeatureData import FeatureData
from features.SessionFeature import SessionFeature
from schemas.Event import Event

class SessionID(SessionFeature):
    def __init__(self, name:str, description:str, sessionID:str):
        SessionFeature.__init__(self, name=name, description=description)
        self._sessionID = sessionID

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return []

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._sessionID]

    # *** Optionally override public functions. ***

