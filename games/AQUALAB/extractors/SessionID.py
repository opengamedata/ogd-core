import typing

from extractors.Feature import Feature
from schemas.Event import Event

class SessionID(Feature):

    def __init__(self):
        min_data_version = None
        max_data_version = None
        super().__init__(min_data_version, max_data_version)
        self._session_id = None

    def _extractFromEvent(self, event:Event) -> None:
        if not self._session_id:
            self._session_id = event.session_id

    def CalculateFinalValues(self) -> typing.Tuple:
        return (self._session_id)
