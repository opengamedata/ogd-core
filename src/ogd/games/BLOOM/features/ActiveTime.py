# import libraries
from datetime import datetime, timedelta
import logging, warnings
from typing import Any, Final, List, Optional, Dict
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData

class ActiveTime(Feature):
    IDLE_LEVEL: Final[int] = 30

    def __init__(self, params: GeneratorParameters, job_map: Dict[str, Any], active_threads: Optional[float] = None):
        self._job_map = job_map
        super().__init__(params=params)
        self._Idle_time: float = 0
        self.active_level: float = active_threads if active_threads else ActiveTime.IDLE_LEVEL
        self._sess_duration: Optional[timedelta] = None
        self._client_start_time: Optional[datetime] = None
        self._client_end_time: Optional[datetime] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["session_start", "pause_game", "unpause_game"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        if event.EventName == "session_start":
            self._client_start_time = event.Timestamp
        elif event.EventName == "pause_game":
            self._client_end_time = event.Timestamp
        elif event.EventName == "unpause_game":
            self._client_start_time = event.Timestamp

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if self._client_start_time and self._client_end_time:
            return [self._client_end_time - self._client_start_time - timedelta(seconds=self._Idle_time)]
        else:
            return ["No events"]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
