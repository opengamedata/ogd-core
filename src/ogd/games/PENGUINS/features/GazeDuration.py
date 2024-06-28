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

class GazeDuration(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._session_id = None
        self._gaze_start_time = None
        self._prev_timestamp = None
        self._time = 0
        self._object_name = None
        self._gaze_dict = dict()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["gaze_object_begin", "gaze_object_end"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return [] 

    def _updateFromEvent(self, event:Event) -> None:
        if event.SessionID != self._session_id:
            self._session_id = event.SessionID
            # if we jumped to a new session, we only want to count time up to last event, not the time between sessions.
            if self._gaze_start_time and self._prev_timestamp:
                self._time += (self._prev_timestamp - self._gaze_start_time).total_seconds()
                self._gaze_start_time = event.Timestamp

        if event.EventName == "gaze_object_begin":
            self._gaze_start_time = event.Timestamp
            self._object_name = event.event_data.get("object_id")
            if not self._object_name in self._gaze_dict.keys():
                self._gaze_dict[self._object_name] = timedelta(0)
        elif event.EventName == "gaze_object_end":
            if self._gaze_start_time is not None:
                self._time += (event.Timestamp - self._gaze_start_time).total_seconds()
                self._gaze_dict[self._object_name]+=timedelta(seconds=self._time)
                self._gaze_start_time = None

        self._prev_timestamp = event.Timestamp



    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._gaze_dict]


    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return [] 
