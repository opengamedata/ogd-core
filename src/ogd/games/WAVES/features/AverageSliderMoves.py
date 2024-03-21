# import libraries
from ogd.core.schemas import Event
from typing import Any, List, Optional
# import locals
from ogd.core.generators.features.SessionFeature import SessionFeature
from ogd.core.generators.Extractor import ExtractorParameters
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData

class AverageSliderMoves(SessionFeature):
    def __init__(self, params:ExtractorParameters):
        SessionFeature.__init__(self, params=params)
        self._levels_encountered : set = set()
        self._slider_count       : int = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.1"]
        # return ["SLIDER_MOVE_RELEASE"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._levels_encountered.add(event.GameState['level']) # set-add level to list, at end we will have set of all levels seen.
        self._slider_count += 1

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if len(self._levels_encountered) > 0:
            return [self._slider_count / len(self._levels_encountered)]
        else:
            return [None]

    # *** Optionally override public functions. ***
