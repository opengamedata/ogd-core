from schemas import Event
import typing
from typing import Any, List, Union
# local imports
from extractors.PerLevelFeature import PerLevelFeature
from schemas.Event import Event

class SequenceLevel(PerLevelFeature):
    def __init__(self, name:str, description:str, count_index:int):
        PerLevelFeature.__init__(self, name=name, description=description, count_index=count_index)
        self._seq = ''
        self._lastSliderType = ''

    def GetEventTypes(self) -> List[str]:
        return ["CUSTOM.1","CUSTOM.2"]
        # return ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"]

    def GetFeatureValues(self) -> Any:
        return self._seq

    def _extractFromEvent(self, event:Event) -> None:
        currentSliderType = event.event_data["slider"]
        if currentSliderType != self._lastSliderType:
            sliderTypeCode = ''
            if currentSliderType == "AMPLITUDE": sliderTypeCode = 'a'
            if currentSliderType == "WAVELENGTH": sliderTypeCode = 'w'
            if currentSliderType == "OFFSET": sliderTypeCode = 'o'
            self._seq = self._seq + sliderTypeCode
        self._lastSliderType = currentSliderType

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None