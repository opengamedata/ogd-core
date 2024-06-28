# import libraries
from datetime import timedelta
from typing import Any, List
# import locals
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

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

    def _updateFromFeatureData(self, feature:FeatureData):
        if feature.PlayerID == self._player_id:
            if feature.FeatureValues[0] == "No events":
                pass
            else:
                self._times.append(feature.FeatureValues[0]/timedelta(seconds=1))

    def _getFeatureValues(self) -> List[Any]:
        if len(self._times) > 0:
            return [sum(self._times) / len(self._times)]
        else:
            return [0]

    # *** Optionally override public functions. ***
