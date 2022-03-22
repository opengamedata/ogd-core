from typing import Any, List

from features.SessionFeature import SessionFeature
from features.FeatureData import FeatureData
from schemas.Event import Event

class UserAvgSessionDuration(SessionFeature):

    def __init__(self, name:str, description:str, player_id:str):
        self._player_id = player_id
        super().__init__(name=name, description=description, count_index=0)
        self._times = []

    def GetEventDependencies(self) -> List[str]:
        return []

    def GetFeatureDependencies(self) -> List[str]:
        return ["SessionDuration"]

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        if feature.PlayerID() == self._player_id:
            self._times.append(feature.FeatureValues()[0])

    def GetFeatureValues(self) -> List[Any]:
        return [sum(self._times) / len(self._times)]
