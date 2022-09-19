# import libraries
from schemas import Event
from typing import Any, List, Optional
# import locals
from extractors.features.Feature import Feature
from schemas.FeatureData import FeatureData
from extractors.features.PerLevelFeature import PerLevelFeature
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event

class PercentAmplitudeMoves(PerLevelFeature):
    def __init__(self, params:ExtractorParameters):
        Feature.__init__(self, params=params)
        self._amplitude_count = 0
        self._count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
def _getEventDependencies(cls, mode:ExportMode) -> List[str]:
        return ["CUSTOM.1", "CUSTOM.2"]
        # return ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"]

    @classmethod
def _getEventDependencies(cls, mode:ExportMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._count += 1
        if event.EventData['slider'].upper() == 'AMPLITUDE':
            self._amplitude_count += 1

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._amplitude_count / self._count if self._count != 0 else None]

    # *** Optionally override public functions. ***
