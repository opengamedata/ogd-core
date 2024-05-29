# import libraries
from ogd.core.models import Event
from typing import Any, List, Optional
# import locals
from ogd.core.generators.extractors.PerLevelFeature import PerLevelFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class SequenceLevel(PerLevelFeature):
    def __init__(self, params:GeneratorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._seq = ''
        self._lastSliderType = ''

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.1","CUSTOM.2"]
        # return ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        currentSliderType = event.EventData["slider"]
        if currentSliderType != self._lastSliderType:
            sliderTypeCode = ''
            if currentSliderType == "AMPLITUDE": sliderTypeCode = 'a'
            if currentSliderType == "WAVELENGTH": sliderTypeCode = 'w'
            if currentSliderType == "OFFSET": sliderTypeCode = 'o'
            self._seq = self._seq + sliderTypeCode
        self._lastSliderType = currentSliderType

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._seq]

    # *** Optionally override public functions. ***