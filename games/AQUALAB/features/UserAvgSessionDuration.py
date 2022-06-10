# import libraries
from typing import Any, List
# import locals
from extractors.features.SessionFeature import SessionFeature
from schemas.FeatureData import FeatureData
from schemas.Event import Event

class UserAvgSessionDuration(SessionFeature):

    def __init__(self, name:str, description:str, player_id:str):
        self._player_id = player_id
        super().__init__(name=name, description=description)
        self._times = []

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return []

    def _getFeatureDependencies(self) -> List[str]:
        return ["SessionDuration"]

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        if feature.PlayerID == self._player_id:
            self._times.append(feature.FeatureValues[0])

    def _getFeatureValues(self) -> List[Any]:
        if len(self._times) > 0:
            return [sum(self._times) / len(self._times)]
        else:
            return [0]

    # *** Optionally override public functions. ***
