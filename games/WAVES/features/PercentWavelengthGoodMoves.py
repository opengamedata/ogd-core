# import libraries
from schemas import Event
from typing import Any, List, Optional
# import locals
from extractors.features.Feature import Feature
from schemas.FeatureData import FeatureData
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event

class PercentWavelengthGoodMoves(Feature):
    def __init__(self, params:ExtractorParameters):
        Feature.__init__(self, params=params)
        self._wavelength_count = 0
        self._good_count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.1", "CUSTOM.2"]
        # return ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"]

    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventData['slider'].upper() == 'WAVELENGTH':
            self._wavelength_count += 1
            if event.EventName == "CUSTOM.1":
                if event.EventData['end_closeness'] > event.EventData['begin_closeness']:
                    self._good_count += 1
            elif event.EventName == "CUSTOM.2":
                start_dist = event.EventData['correct_val'] - event.EventData['begin_val']
                end_dist = event.EventData['correct_val'] - event.EventData['end_val']
                if abs(end_dist) < abs(start_dist):
                    self._good_count += 1

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._good_count / self._wavelength_count if self._wavelength_count != 0 else None]

    # *** Optionally override public functions. ***
