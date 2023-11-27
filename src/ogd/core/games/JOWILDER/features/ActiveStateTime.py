# import libraries
import json
from time import time
from typing import Any, List, Optional
from datetime  import timedelta, datetime
# import local files
from extractors.Extractor import ExtractorParameters
from extractors.features.SessionFeature import SessionFeature
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
from schemas.Event import Event

class ActiveStateTime(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """

    ACTIVE_TIME_THRESHOLD = timedelta(seconds=15)
    CLICK_EVENTS_NAME = [f"CUSTOM.{i}" for i in range(3, 12)]

    def __init__(self, params:ExtractorParameters, threshold:int):
        super().__init__(params=params)
        self._time : timedelta = timedelta(0)
        self._clicking_time : timedelta = timedelta(0)
        self._last_hover_or_click_timestamp : Optional[datetime] = None
        self._last_click_timestamp : Optional[datetime] = None
        self._threshold = timedelta(seconds = threshold)


    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return [f"CUSTOM.{i}" for i in range(3, 21)] + ["CUSTOM.1"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventName == "CUSTOM.1" and not self._last_hover_or_click_timestamp:
            self._last_hover_or_click_timestamp = event.Timestamp
            self._last_click_timestamp = event.Timestamp
            return
        # elif event.EventName == "CUSTOM.1" or not self._last_hover_or_click_timestamp:
        #     raise(ValueError("Multiple game start events or none gamestart events!"))

        if self._last_hover_or_click_timestamp is not None:
            _time_between_hover_or_click = event.Timestamp - self._last_hover_or_click_timestamp
            if _time_between_hover_or_click < self._threshold:
                self._time += _time_between_hover_or_click
            self._last_hover_or_click_timestamp = event.Timestamp

        if self._last_click_timestamp is not None:
            if event.EventName in ActiveStateTime.CLICK_EVENTS_NAME:
                _time_between_click = event.Timestamp - self._last_click_timestamp
                if _time_between_click < self._threshold:
                    self._clicking_time += _time_between_click
                self._last_click_timestamp = event.Timestamp

        return

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._time, self._clicking_time]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["Clicking"] # >>> fill in names of Subfeatures for which this Feature should extract values. <<<
    
