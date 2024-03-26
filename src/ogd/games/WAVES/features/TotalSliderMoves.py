# import libraries
from ogd.core.schemas import Event
from typing import Any, List, Optional
# import locals
from ogd.core.generators.extractors.PerLevelFeature import PerLevelFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData

class TotalSliderMoves(PerLevelFeature):
    def __init__(self, params:GeneratorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._slider_move_count : int = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.1"]
        # return ["SLIDER_MOVE_RELEASE"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
            self._slider_move_count += 1

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._slider_move_count]

    # *** Optionally override public functions. ***
