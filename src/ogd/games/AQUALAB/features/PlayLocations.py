import logging
from datetime import timedelta
from typing import Any, List

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData


class PlayLocations(SessionFeature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)

        # Track seen sessions and in-school sessions
        self._seen_sessions = set()
        self._session_locations = []
        self._session_times = []

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["all_events"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []
    
    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _updateFromEvent(self, event: Event) -> None:
        if not event.SessionID in self._seen_sessions:
            self._seen_sessions.add(event.SessionID)

            # Use event.Timestamp directly for time checks
            aware_time = event.Timestamp.replace(tzinfo=event.TimeOffset)
            self._session_times.append(aware_time)

            local_time = aware_time + (aware_time.utcoffset() or timedelta(0))
            # Determine if the session is during school hours
            is_weekday = local_time.weekday() < 5  
            is_school_hours = 9 <= local_time.hour < 15

            # Set in_school based on weekday and time criteria
            in_school = "SCHOOL" if is_weekday and is_school_hours else "HOME"
            self._session_locations.append(in_school)

    def _getFeatureValues(self) -> List[Any]:
        start_in_school = self._session_locations[0] == "SCHOOL" if len(self._session_locations) > 0 else False
        resumed_at_home = "HOME" in self._session_locations[1:] if len(self._session_locations) > 0 else False
        converted = start_in_school and resumed_at_home
        return [self._session_locations, self._session_times, converted]

    def Subfeatures(self) -> List[str]:
        return ["SessionLocalTimes", "SchoolToHomeConversion"]

    @classmethod
    def AvailableModes(cls) -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER]
