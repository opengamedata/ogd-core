# import libraries   
import logging
from datetime import timedelta
from typing import Any, List

# import locals
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.common.models.Event import Event, EventSource
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from ogd.common.utils.Logger import Logger

class TotalSessionTime(SessionFeature):

    def __init__(self, params: GeneratorParameters, threshold: int = 30):
        super().__init__(params=params)
        self.threshold = timedelta(seconds=threshold)
        self.previous_time = None
        self.idle_time = timedelta(0)
        self.total_session_time = timedelta(0)

    def Subfeatures(self) -> List[str]:
        return ["Seconds", "Active", "ActiveSeconds", "Idle" "IdleSeconds"]

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["all_events"]
    
    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

# For each event, it calculates the time difference from the previous event,
# determines if it’s idle or active time, and updates the total session time and idle time accordingly
    def _updateFromEvent(self, event: Event) -> None:
        if event.EventSource == EventSource.GAME:
            if self.previous_time is not None:
                # Calculate time difference since the last event
                time_diff = event.Timestamp - self.previous_time
                self.total_session_time += time_diff

                # Determine if time_diff is idle or active
                if time_diff > self.threshold:
                    self.idle_time += time_diff
                
            # Update previous_time for the next event
            self.previous_time = event.Timestamp

    def _updateFromFeatureData(self, feature:FeatureData):
        return
    
    def _getFeatureValues(self) -> List[Any]:
        active_time = self.total_session_time - self.idle_time
        return [
            str(self.total_session_time),
            self.total_session_time.total_seconds(),
            str(active_time),
            active_time.total_seconds(),
            str(self.idle_time),
            self.idle_time.total_seconds()
        ]

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.SESSION]
    