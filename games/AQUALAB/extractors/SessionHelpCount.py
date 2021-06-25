import typing

from extractors.Feature import Feature
from schemas.Event import Event

class SessionHelpCount(Feature):

    def __init__(self):
        min_data_version = None
        max_data_version = None
        super().__init__(min_data_version, max_data_version)
        self._count = 0

    def _extractFromEvent(self, event:Event) -> None:
        self._count += 1

    def CalculateFinalValues(self) -> typing.Tuple:
        return (self._count)
