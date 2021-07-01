from schemas import Event
import typing
from typing import Any, Union
# local imports
from extractors.Feature import Feature
from schemas.Event import Event

class AmplitudeGoodMoveCount(Feature):
    def __init__(self, name:str, description:str, min_version:Union[str,None]=None, max_version:Union[str,None]=None):
        Feature.__init__(self, name, description, min_version, max_version)
        self._count = 0

    def CalculateFinalValues(self) -> typing.Any:
        return self._count

    def _extractFromEvent(self, event:Event):
        self._count += 1
        if event.event_data['slider'] == 'Amplitude':
            if event.event_data['closeness_end'] > event.event_data['closeness_start']:
                self._count += 1
