# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.Extractor import ExtractorParameters
from ogd.core.generators.features.Feature import Feature
from ogd.games.PENGUINS.features.PerRegionFeature import PerRegionFeature
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData
from ogd.core.generators.features.SessionFeature import SessionFeature


class PlayerWaddleCount(SessionFeature):

    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._current_count : int = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["player_waddle"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._current_count += 1

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._current_count]

    