import typing
from datetime import timedelta

from extractors.Feature import Feature
from schemas.Event import Event

class SessionDuration(Feature):

    def __init__(self):
        min_data_version = None
        max_data_version = None
        super().__init__(min_data_version, max_data_version)
        self._client_start_time = None
        self._session_duration = timedelta(0)

    def _extractFromEvent(self, event:Event) -> None:
        if not self._client_start_time:
            self._client_start_time = event.timestamp

        self._session_duration = event.timestamp - self._client_start_time

    def CalculateFinalValues(self) -> typing.Tuple:
        return (self._session_duration)
