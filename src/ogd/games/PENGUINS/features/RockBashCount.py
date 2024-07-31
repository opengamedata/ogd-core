# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.generators.extractors.SessionFeature import SessionFeature


class RockBashCount(SessionFeature):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._current_count : int = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["flipper_bash_rock"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        self._current_count += 1

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._current_count]
