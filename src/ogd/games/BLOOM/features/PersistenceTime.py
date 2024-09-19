from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event, EventSource
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
import time

class PersistenceTime(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.has_lost: bool = False
        self.last_time: Optional[datetime] = None
        self.running_time : timedelta = timedelta(0)
        self.total_seconds_list: List[float] = []

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["all_events"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        # If player didn't lose yet, skip (unless this event is a loss)
        if not self.has_lost:
            if event.EventName == "lose_game":
                self.has_lost = True
        # Otherwise, if had new session/game start since last event, just skip without counting.
        elif event.EventName in ["session_start", "game_start"]:
            self.last_time = event.Timestamp
            return
        # Otherwise, handle any events that came from the game itself.
        elif event.EventSource == EventSource.GAME:
            if self.last_time is not None:
                event_duration = event.Timestamp - self.last_time
                self.running_time += event_duration
            # If we got a win or a loss, reset timer
            if event.EventName in ["win_game", "lose_game"]:
                self.total_seconds_list.append(self.running_time.total_seconds())
                self.running_time = timedelta(0)
            self.last_time = event.Timestamp

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [sum(self.total_seconds_list), self.total_seconds_list]

    # Subfeature breakdown
    def Subfeatures(self) -> List[str]:
        return ["PersistenceTimeList"]

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER, ExtractionMode.SESSION]

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
