# import libraries
from datetime import timedelta
from typing import Any, List
# import locals
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature

class UserAvgActiveTime(SessionFeature):

    def __init__(self, params:GeneratorParameters, player_id:str):
        self._player_id = player_id
        super().__init__(params=params)
        self._times : List[float] = []

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["ActiveTime"]

    def _updateFromEvent(self, event:Event) -> None:
        return

    def _updateFromFeature(self, feature:Feature):
        if feature.PlayerID == self._player_id:
            if feature.Values[0] == "No events":
                pass
            else:
                self._times.append(feature.Values[0]/timedelta(seconds=1))

    def _getFeatureValues(self) -> List[Any]:
        if len(self._times) > 0:
            return [sum(self._times) / len(self._times)]
        else:
            return [0]

    # *** Optionally override public functions. ***
