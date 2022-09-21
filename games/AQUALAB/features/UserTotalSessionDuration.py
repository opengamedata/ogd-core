from datetime import timedelta
from typing import Any, List

from extractors.Extractor import ExtractorParameters
from extractors.features.SessionFeature import SessionFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData

class UserTotalSessionDuration(SessionFeature):
    """_summary_

    :param SessionFeature: _description_
    :type SessionFeature: _type_
    """
    def __init__(self, params:ExtractorParameters, player_id:str):
        super().__init__(params=params)
        self._player_id = player_id
        self._time = timedelta(0)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["SessionDuration"]

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature:FeatureData):
        if feature.PlayerID == self._player_id:
            if type(feature.FeatureValues[0]) == str and feature.FeatureValues[0] == "No events":
                pass
            else:
                self._time += feature.FeatureValues[0]

    def _getFeatureValues(self) -> List[Any]:
        return [self._time.seconds]

    # *** Optionally override public functions. ***
