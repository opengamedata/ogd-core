# import libraries
import logging
from datetime import datetime, timedelta
from typing import Any, List
# import locals
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.utils.Logger import Logger

class SessionDuration(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:GeneratorParameters, session_id:str):
        self._session_id = session_id
        super().__init__(params=params)
        self._start_time = None
        self._start_index = None
        self._latest_event = None
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
        if not self._start_time:
            self._start_time = event.Timestamp
            self._start_index = event.EventSequenceIndex
        if self._start_time > event.Timestamp + timedelta(milliseconds=100):
            # Logger.Log(f"Got out-of-order events in SessionDuration; event {event.EventName}:{event.EventSequenceIndex} for player {event.UserID}:{event.SessionID} had timestamp {event.Timestamp} earlier than start event, with time {self._start_time}, index {self._start_index}!", logging.WARN)
            self._start_time = event.Timestamp
            self._start_index = event.EventSequenceIndex
        # if this was the latest event, make it the end time, otherwise output error.
        if self._latest_event is not None and self._latest_event.Timestamp > event.Timestamp + timedelta(milliseconds=100):
            # Logger.Log(f"Got out-of-order events in SessionDuration:\n   Event {event.EventName}:{event.EventSequenceIndex} for player {event.UserID}:{event.SessionID} had timestamp {event.Timestamp},\n   Earlier than previous latest event {self._latest_event.EventName}:{self._latest_event.EventSequenceIndex} for player {self._latest_event.UserID}:{self._latest_event.SessionID} with timestamp {self._latest_event.Timestamp}", logging.WARN)
            pass
        else:
            self._latest_event = event
        # self._session_duration = (event.Timestamp - self._client_start_time).total_seconds()

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if self._start_time and self._latest_event:
            return [self._latest_event.Timestamp - self._start_time]
        else:
            return ["No events"]

    # *** Optionally override public functions. ***

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.SESSION]