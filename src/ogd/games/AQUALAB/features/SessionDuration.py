# import libraries
import logging
from datetime import timedelta
from typing import Any, List
# import locals
from ogd.core.extractors.Extractor import ExtractorParameters
from ogd.core.extractors.features.SessionFeature import SessionFeature
from ogd.core.schemas.Event import Event, EventSource
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData
from ogd.core.utils.Logger import Logger

class SessionDuration(SessionFeature):

    def __init__(self, params:ExtractorParameters, threshold:int):
        self.threshold = threshold
        super().__init__(params=params)
        self.max_idle = timedelta(0)
        self.previous_time = None
        self.idle_time = timedelta(0)
        self.total_session_time = timedelta(0)
        # self._session_duration = 0
    def Subfeatures(self) -> List[str]:
            return ["Total", "- Seconds", "Active", "Active - Seconds", "Idle" "Idle - Seconds", "Max-Idle"]
    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["all_events"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventSource == EventSource.GAME:
            if self.previous_time is not None:
                self.total_session_time += (event.Timestamp - self.previous_time)
                if (event.Timestamp - self.previous_time) > timedelta(minutes=1):
                    self.idle_time += (event.Timestamp - self.previous_time)
                    if self.max_idle < (event.Timestamp - self.previous_time):
                        self.max_idle = event.Timestamp - self.previous_time
            self.previous_time = event.Timestamp
                

     
    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if self.total_session_time is not None:
            return [self.total_session_time, self.total_session_time.total_seconds(), (self.total_session_time - self.idle_time), (self.total_session_time - self.idle_time).total_seconds(), self.idle_time, self.idle_time.total_seconds(), self.max_idle]
        else:
            return ["No events"]

    # *** Optionally override public functions. ***

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.SESSION]
