# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData
from ogd.core.generators.extractors.SessionFeature import SessionFeature


class LogVersion(SessionFeature):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._current_log : str = "UNKNOWN LOG VERSION"

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["all_events"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        self._current_log = event.LogVersion


    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._current_log]

    