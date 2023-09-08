# import libraries
import logging
from typing import Any, List
# import locals
from extractors.Extractor import ExtractorParameters
from extractors.features.SessionFeature import SessionFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
from utils.Logger import Logger

# import libraries
import logging
from typing import Any, List, Optional
from datetime import datetime, timedelta
# import locals
from extractors.Extractor import ExtractorParameters
from extractors.features.SessionFeature import SessionFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
from utils.Logger import Logger

class SessionDuration(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:ExtractorParameters, session_id:str):
        self._session_id = session_id
        super().__init__(params=params)
        self._client_start_time = None
        self._client_end_time = None
        self._client_start_index = None
        self._client_end_index = None
        self._session_duration = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["all_events"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return [] 

    def _extractFromEvent(self, event:Event) -> None:
        if not self._client_start_time:
            self._client_start_time = event.Timestamp
            self._client_start_index = event.EventSequenceIndex
        if self._client_start_time > event.Timestamp:
            Logger.Log(f"Got out-of-order events in SessionDuration; event {event.EventName}:{event.EventSequenceIndex} for session {event.SessionID} had timestamp {event.Timestamp} earlier than start event, with time {self._client_start_time}, index {self._client_start_index}!", logging.WARN)
            self._client_start_time = event.Timestamp
            self._client_start_index = event.EventSequenceIndex
        # if this was the latest event, make it the end time, otherwise output error.
        if self._client_end_time is not None and self._client_end_time > event.Timestamp:
            Logger.Log(f"Got out-of-order events in SessionDuration; event {event.EventName}:{event.EventSequenceIndex} for player {event.UserID}:{event.SessionID} had timestamp {event.Timestamp} earlier than end event, with time {self._client_end_time}, index {self._client_end_index}!", logging.WARN)
        else:
            self._client_end_time = event.Timestamp
            self._client_end_index = event.EventSequenceIndex

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if self._client_start_time and self._client_end_time:
            return [self._client_end_time - self._client_start_time]
        else:
            return ["No events"]

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.SESSION]


    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return [] 
