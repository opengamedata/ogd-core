from schemas import Event
import typing
from typing import Any, List, Union
# local imports
from extractors.SessionFeature import SessionFeature
from schemas.Event import Event

class OverallPercentWavelengthMoves(SessionFeature):
    def __init__(self, name:str, description:str):
        SessionFeature.__init__(self, name=name, description=description)
        self._wavelength_count = 0
        self._move_count = 0

    def GetEventTypes(self) -> List[str]:
        return ["CUSTOM.1", "CUSTOM.2"]
        # return ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"]

    def CalculateFinalValues(self) -> Any:
        return self._wavelength_count / self._move_count * 100

    def _extractFromEvent(self, event:Event) -> None:
        self._move_count += 1
        if event.event_data["slider"] == "WAVELENGTH":
            self._wavelength_count += 1

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None


