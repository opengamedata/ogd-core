from schemas import Event
import typing
from typing import Any, List, Union
# local imports
from extractors.Feature import Feature
from schemas.Event import Event

class AmplitudeGoodMoveCount(Feature):
    def __init__(self, name:str, description:str, count_index:int=0):
        Feature.__init__(self, name=name, description=description, count_index=count_index)
        self._count = 0

    def CalculateFinalValues(self) -> typing.Any:
        return self._count

    def _extractFromEvent(self, event:Event):
        self._count += 1
        if event.event_data['slider'] == 'Amplitude':
            if event.event_data['closeness_end'] > event.event_data['closeness_start']:
                self._count += 1

    def GetEventTypes(self) -> List[str]:
        return ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"]

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None