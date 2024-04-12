# import libraries
import logging
from typing import Any, List
# import locals
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData
from ogd.core.utils.Logger import Logger

class SessionDuration(SessionFeature):

    def __init__(self, params:GeneratorParameters, session_id:str):
        self._session_id = session_id
        super().__init__(params=params)
        self._client_start_time = None
        self._client_start_index = None
        self._client_end_time = None
        self._client_end_index = None
        # self._session_duration = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["all_events"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        # if this was earliest event, make it the start time.
        if not self._client_start_time:
            self._client_start_time = event.Timestamp
            self._client_start_index = event.EventSequenceIndex
        if self._client_start_time > event.Timestamp:
            Logger.Log(f"Got out-of-order events in SessionDuration for session {self._session_id};\nevent {event.EventName}:{event.EventSequenceIndex} for player {event.UserID}:{event.SessionID} had timestamp {event.Timestamp} earlier than start event, with time {self._client_start_time}, index {self._client_start_index}!", logging.WARN)
            self._client_start_time = event.Timestamp
            self._client_start_index = event.EventSequenceIndex
        # if this was the latest event, make it the end time, otherwise output error.
        if self._client_end_time is not None and self._client_end_time > event.Timestamp:
            Logger.Log(f"Got out-of-order events in SessionDuration for session {self._session_id};\nevent {event.EventName}:{event.EventSequenceIndex} for player {event.UserID}:{event.SessionID} had timestamp {event.Timestamp} earlier than end event, with time {self._client_end_time}, index {self._client_end_index}!", logging.WARN)
        else:
            self._client_end_time = event.Timestamp
            self._client_end_index = event.EventSequenceIndex
        # self._session_duration = (event.Timestamp - self._client_start_time).total_seconds()

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if self._client_start_time and self._client_end_time:
            return [self._client_end_time - self._client_start_time]
        else:
            return ["No events"]

    # *** Optionally override public functions. ***

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.SESSION]
