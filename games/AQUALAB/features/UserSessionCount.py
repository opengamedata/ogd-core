# global imports
from typing import Any, List
# local imports
from features.SessionFeature import SessionFeature
from features.FeatureData import FeatureData
from schemas.Event import Event

class UserSessionCount(SessionFeature):

    def __init__(self, name:str, description:str, player_id:str):
        self._player_id = player_id
        super().__init__(name=name, description=description)
        self._count = 0

    # *** Implement abstract functions ***
    def _getEventDependencies(self) -> List[str]:
        return []

    def _getFeatureDependencies(self) -> List[str]:
        return ["SessionID"]

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        if feature.PlayerID() == self._player_id:
            self._count += 1

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***
