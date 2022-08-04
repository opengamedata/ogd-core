# import libraries
from schemas import Event
import typing
from typing import Any, List, Optional
# import locals
from schemas.FeatureData import FeatureData
from extractors.features.PerLevelFeature import PerLevelFeature
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event

class SliderAverageRange(PerLevelFeature):
    def __init__(self, params:ExtractorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._ranges = []

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["CUSTOM.1"]
        # return ["SLIDER_MOVE_RELEASE"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._ranges.append(event.EventData["max_val"] - event.EventData["min_val"])

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if len(self._ranges) > 0:
            return [sum(self._ranges) / len(self._ranges)]
        else:
            return [None]

    # *** Optionally override public functions. ***
