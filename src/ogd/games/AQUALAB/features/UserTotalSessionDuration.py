from datetime import timedelta
from typing import Any, List

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class UserTotalSessionDuration(SessionFeature):
    """_summary_

    :param SessionFeature: _description_
    :type SessionFeature: _type_
    """
    def __init__(self, params:GeneratorParameters, player_id:str):
        super().__init__(params=params)
        self._player_id = player_id
        self._time = timedelta(0)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["SessionDuration"]

    def _updateFromEvent(self, event:Event) -> None:
        return

    def _updateFromFeatureData(self, feature:FeatureData):
        if feature.PlayerID == self._player_id:
            if type(feature.FeatureValues[0]) == str and feature.FeatureValues[0] == "No events":
                pass
            else:
                self._time += feature.FeatureValues[0]

    def _getFeatureValues(self) -> List[Any]:
        return [self._time.total_seconds()]

    # *** Optionally override public functions. ***
