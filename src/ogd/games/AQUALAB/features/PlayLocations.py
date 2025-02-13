import logging
from typing import Any, List

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData


class PlayLocations(SessionFeature):

    @classmethod
    def _getEventDependencies(cls, mode: ExtractionMode) -> List[str]:
        return ["all_events"]

    @classmethod
    def _getFeatureDependencies(cls, mode: ExtractionMode) -> List[str]:
        return []
    
    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _extractFromEvent(self, event: Event) -> None:
        if not event.SessionID in self._seen_sessions:
            self._seen_sessions.add(event.SessionID)

            # Use event.Timestamp directly for time checks
            session_time = event.Timestamp
            self._session_times.append(session_time)

            # Determine if the session is during school hours
            is_weekday = session_time.weekday() < 5  
            is_school_hours = 9 <= session_time.hour < 15

            # Set in_school based on weekday and time criteria
            in_school = is_weekday and is_school_hours
            self._in_school_sessions.append(in_school)

    def _getFeatureValues(self) -> List[Any]:
        return [self._in_school_sessions, self._session_times]

    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)

        # Track seen sessions and in-school sessions
        self._seen_sessions = set()
        self._in_school_sessions = []
        self._session_times = []

    def Subfeatures(self) -> List[str]:
        return ["LocalTime"]

    @classmethod
    def AvailableModes(cls) -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER]
