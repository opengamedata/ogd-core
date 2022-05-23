# import libraries
from schemas import Event
from typing import Any, List, Optional
# import locals
from schemas.FeatureData import FeatureData
from features.PerLevelFeature import PerLevelFeature
from schemas.Event import Event

class SequenceLevel(PerLevelFeature):
    def __init__(self, name:str, description:str, count_index:int):
        PerLevelFeature.__init__(self, name=name, description=description, count_index=count_index)
        self._seq = ''
        self._lastSliderType = ''

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["CUSTOM.1","CUSTOM.2"]
        # return ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"]

    def _getFeatureDependencies(self) -> List[str]:
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

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._seq]

    # *** Optionally override public functions. ***