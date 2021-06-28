from schemas import Event
import typing
from typing import Union
# local imports
from extractors.Feature import Feature
from schemas.Event import Event

class AmplitudeGoodMoveCount(Feature):
    def __init__(self):
        min_data_version = None
        max_data_version = None
        Feature.__init__(self, min_data_version, max_data_version)
        self._count = 0

    def CalculateFinalValues(self) -> typing.Tuple:
        return (self._count)

    def _extractFromEvent(self, event:Event):
        self._count += 1
        if event.event_data['slider'] == 'Amplitude':
            if event.event_data['closeness_end'] > event.event_data['closeness_start']:
                self._count += 1
