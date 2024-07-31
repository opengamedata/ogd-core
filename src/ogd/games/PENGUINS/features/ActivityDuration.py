# import libraries
import logging
from typing import Any, List, Optional
from datetime import datetime, timedelta
# import locals
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.utils.Logger import Logger

class ActivityDuration(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._session_id = None
        self._activity_start_time = None
        self._prev_timestamp = None
        self._time = 0
        self._activity_name = None
        self._activity_dict = dict()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["activity_begin", "activity_end"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return [] 

    def _updateFromEvent(self, event:Event) -> None:
        if event.SessionID != self._session_id:
            self._session_id = event.SessionID
            # if we jumped to a new session, we only want to count time up to last event, not the time between sessions.
            if self._activity_start_time and self._prev_timestamp:
                self._time += (self._prev_timestamp - self._activity_start_time).total_seconds()
                self._activity_start_time = event.Timestamp

        if event.EventName == "activity_begin":
            self._activity_start_time = event.Timestamp
            self._activity_name = event.event_data.get("activity_name")
            if not self._activity_name in self._activity_dict.keys():
                self._activity_dict[self._activity_name] = timedelta(0)
        elif event.EventName == "activity_end":
            if self._activity_start_time is not None:
                self._time += (event.Timestamp - self._activity_start_time).total_seconds()
                self._activity_dict[self._activity_name]+=timedelta(seconds=self._time)
                self._activity_start_time = None

        self._prev_timestamp = event.Timestamp



    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._activity_dict]


    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return [] 