# import libraries
from ogd.core.schemas import Event
from typing import Any, List, Optional
# import locals
from ogd.core.extractors.features.PerLevelFeature import PerLevelFeature
from ogd.core.extractors.Extractor import ExtractorParameters
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData

class SequenceLevel(PerLevelFeature):
    def __init__(self, params:ExtractorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._seq = ''
        self._lastSliderType = ''

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.1","CUSTOM.2"]
        # return ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        currentSliderType = event.EventData["slider"]
        if currentSliderType != self._lastSliderType:
            sliderTypeCode = ''
            if currentSliderType == "AMPLITUDE": sliderTypeCode = 'a'
            if currentSliderType == "WAVELENGTH": sliderTypeCode = 'w'
            if currentSliderType == "OFFSET": sliderTypeCode = 'o'
            self._seq = self._seq + sliderTypeCode
        self._lastSliderType = currentSliderType

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._seq]

    # *** Optionally override public functions. ***