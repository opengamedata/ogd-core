from typing import Any, List

from extractors.Extractor import ExtractorParameters
from extractors.features.SessionFeature import SessionFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData


class InSchoolSessions(SessionFeature):
    """A feature that determines whether a session started in school or not."""

    def __init__(self, params: ExtractorParameters):
        super().__init__(params=params)

        # The list of sessions that have been seen before.
        self._seen_sessions = []
        # The list of sessions that started in school.
        self._in_school_sessions = []

    @classmethod
    def AvailableModes(cls) -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER]

    def _extractFromEvent(self, event: Event) -> None:
        """Checking if the event is the first event in a session, and if so, whether it started in school."""
        session_id = event.SessionID
        if session_id not in self._seen_sessions:
            # This is the first event in a new session.
            is_in_school = event.Timestamp.weekday() < 5 and 9 <= event.Timestamp.hour <= 15
            self._seen_sessions.append(session_id)
            self._in_school_sessions.append(is_in_school)

    def _getFeatureValues(self) -> List[Any]:
        """Return the list of sessions that started in school."""
        return self._in_school_sessions
    


"""
FOR LOCALTIME TRIAL:


from typing import Any, List

from extractors.Extractor import ExtractorParameters
from extractors.features.SessionFeature import SessionFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData


class InSchoolSessions(SessionFeature):
   #A feature that determines whether a session started in school or not.

    def __init__(self, params: ExtractorParameters):
        super().__init__(params=params)

        # The list of sessions that have been seen before.
        self._seen_sessions = []
        # The list of sessions that started in school.
        self._in_school_sessions = []

    @classmethod
    def AvailableModes(cls) -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER]

    def _extractFromEvent(self, event: Event) -> None:
        #Checking if the event is the first event in a session, and if so, whether it started in school
        session_id = event.SessionID
        if session_id not in self._seen_sessions:
            # This is the first event in a new session.
            local_time = YOUR_LOCALTIME_CONVERTER_FUNCTION_HERER(event.Timestamp)
            is_in_school = local_time.weekday() < 5 and 9 <= local_time.hour <= 15
            self._seen_sessions.append(session_id)
            self._in_school_sessions.append(is_in_school)

    def _getFeatureValues(self) -> List[Any]:
        #Return the list of sessions that started in school
        return self._in_school_sessions






"""