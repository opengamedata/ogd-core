# import libraries
from datetime import datetime, timedelta
from typing import Any, Final, List, Optional
# import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event, EventSource
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

class ActiveTime(Feature):
    DEFAULT_IDLE_THRESHOLD: Final[timedelta] = timedelta(seconds=30)

    def __init__(self, params: GeneratorParameters, idle_threshold: Optional[int]):
        super().__init__(params=params)
        self.IDLE_THRESHOLD     : Final[timedelta] = timedelta(seconds=idle_threshold) if idle_threshold is not None else ActiveTime.DEFAULT_IDLE_THRESHOLD
        self.max_idle           : timedelta = timedelta(0)
        self.previous_time      : Optional[datetime] = None
        self.idle_time          : timedelta = timedelta(0)
        self.total_session_time : timedelta = timedelta(0)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["session_start", "all_events"]

    def Subfeatures(self) -> List[str]:
        return ["Total", "Seconds", "ActiveSeconds", "Idle", "IdleSeconds", "MaxIdle"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        if event.EventSource == EventSource.GAME:
            if self.previous_time is not None:
                event_duration = event.Timestamp - self.previous_time
                self.total_session_time += event_duration
                if event_duration > self.IDLE_THRESHOLD:
                    self.idle_time += event_duration
                    if event_duration > self.max_idle:
                        self.max_idle = event_duration
            self.previous_time = event.Timestamp

        if event.EventName == "session_start":
            self.previous_time = event.Timestamp

    def _updateFromFeatureData(self, feature: FeatureData):
        pass

    def _getFeatureValues(self) -> List[Any]:
        active_time = self.total_session_time - self.idle_time
        return [
            active_time,
            self.total_session_time,
            self.total_session_time.total_seconds(),
            active_time.total_seconds(),
            self.idle_time,
            self.idle_time.total_seconds(),
            self.max_idle
        ]

    # *** Optionally override public functions ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
