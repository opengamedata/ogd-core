# import libraries
import logging
from datetime import timedelta
from typing import Any, List

# import locals
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.common.models.Event import Event, EventSource
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature
from ogd.common.utils.Logger import Logger

class TotalPopulationTime(SessionFeature):

    def __init__(self, params: GeneratorParameters, threshold: int = 30):
        super().__init__(params=params)
        self.threshold = timedelta(seconds=threshold)
        self.total_population_time = timedelta(0)
        self.total_idle_time = timedelta(0)
        self.previous_time = None
        self.previous_session_id = None
        self.previous_player_id = None
 
    def Subfeatures(self) -> List[str]:
        return ["Seconds", "Active", "ActiveSeconds", "Idle", "IdleSeconds"]

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["all_events"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        # Ignore events with missing timestamps
        if not event.Timestamp:
            Logger.Log(
                f"Skipping event with missing timestamp: {event}",
                level=logging.WARNING,
            )
            return

        # Check for session or player ID changes
        if (
            self.previous_session_id != event.SessionID
            or self.previous_player_id != event.user_id
        ):
            Logger.Log(
                f"Session or Player ID changed. Ignoring time contribution. "
                f"Previous: (SessionID={self.previous_session_id}, PlayerID={self.previous_player_id}), "
                f"Current: (SessionID={event.SessionID}, PlayerID={event.user_id})",
                level=logging.INFO,
            )
            # Update IDs without updating time contributions
            self.previous_session_id = event.SessionID
            self.previous_player_id = event.user_id
            self.previous_time = event.Timestamp
            return

        # Calculate time difference and update total population time
        if self.previous_time:
            time_diff = event.Timestamp - self.previous_time
            if time_diff > timedelta(0):  # Only consider positive time intervals
                self.total_population_time += time_diff

                # Determine if the time_diff counts as idle
                if time_diff > self.threshold:
                    self.total_idle_time += time_diff

        # Update previous state variables
        self.previous_time = event.Timestamp

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        active_time = self.total_population_time - self.total_idle_time
        return [
            str(self.total_population_time),
            self.total_population_time.total_seconds(),
            str(active_time),
            active_time.total_seconds(),
            str(self.total_idle_time),
            self.total_idle_time.total_seconds()
        ]

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.POPULATION]
