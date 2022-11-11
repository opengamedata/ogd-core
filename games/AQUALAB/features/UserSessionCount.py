# import libraries
from typing import Any, List
# import locals
from extractors.Extractor import ExtractorParameters
from extractors.features.SessionFeature import SessionFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData

class UserSessionCount(SessionFeature):

    def __init__(self, params:ExtractorParameters, player_id:str):
        self._player_id = player_id
        super().__init__(params=params)
        self._count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["SessionID"]

    def _extractFromEvent(self, event:Event) -> None:
        return

    def _extractFromFeatureData(self, feature:FeatureData):
        if feature.ExportMode == ExtractionMode.SESSION and feature.PlayerID == self._player_id:
            self._count += 1

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        """List of ExtractionMode supported by the Feature.

        Overridden from base Feature version.
        A PlayerSummary is only used at player and population levels; not concerned with session-level.
        :return: _description_
        :rtype: List[ExtractionMode]
        """
        return [ExtractionMode.PLAYER]
