# import libraries
from schemas import Event
import typing
from typing import Any, List, Optional
# import locals
from schemas.FeatureData import FeatureData
from extractors.features.PerLevelFeature import PerLevelFeature
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event

class TotalMoveTypeChanges(PerLevelFeature):
    def __init__(self, params:ExtractorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._last_move = None
        self._change_count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.1", "CUSTOM.2"]
        # return ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"]

    @classmethod
def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if self._last_move != event.EventName:
            self._change_count += 1
        self._last_move = event.EventName

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._change_count]

    # *** Optionally override public functions. ***
