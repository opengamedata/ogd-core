# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from utils import Logger
from datetime import datetime, timedelta
from extractors.Extractor import ExtractorParameters
from extractors.features.Feature import Feature
from games.PENGUINS.features.PerRegionFeature import PerRegionFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
from extractors.features.SessionFeature import SessionFeature

class MirrorWaddleDuration(SessionFeature):
    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._session_id = None
        self._argument_start_time : Optional[datetime] = None
        self._prev_timestamp = None
        self._time = 0
        self._waddle_count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["enter_region", "player_waddle",'begin']

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.SessionID != self._session_id:
            self._session_id = event.SessionID
            # if we jumped to a new session, we only want to count time up to last event, not the time between sessions.
            if self._argument_start_time and self._prev_timestamp:
                self._time += (self._prev_timestamp - self._argument_start_time).total_seconds()
                self._argument_start_time = event.Timestamp

        if event.EventName == "begin":
            self._argument_start_time = event.Timestamp
            self._waddle_count = 0
        elif self._argument_start_time is not None:
            if event.event_name == "player_waddle":
                self._waddle_count += 1
            if event.EventName == "enter_region":
                if event.event_data.get("region_name") == "Mirror":
                    self._time = (event.Timestamp - self._argument_start_time).total_seconds()
                    self._argument_start_time = None
                    return
        self._prev_timestamp = event.Timestamp
    
    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [{"waddle":self._waddle_count, "duration": self._time}]

    
    # def __init__(self, params:ExtractorParameters):
    #     super().__init__(params=params)
    #     self._session_id = None
    #     self._argument_start_time : Optional[datetime] = None
    #     self._prev_timestamp = None
    #     self._time = 0
    #     self._waddle_count = 0
    #     self._waddle_detector_dict = dict()

    # # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    # @classmethod
    # def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
    #     return ["enter_region", "player_waddle",'begin']

    # @classmethod
    # def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
    #     return []

    # def _extractFromEvent(self, event:Event) -> None:
    #     if event.SessionID != self._session_id:
    #         self._session_id = event.SessionID
    #         # if we jumped to a new session, we only want to count time up to last event, not the time between sessions.
    #         if self._argument_start_time and self._prev_timestamp:
    #             self._time += (self._prev_timestamp - self._argument_start_time).total_seconds()
    #             self._argument_start_time = event.Timestamp

    #     if event.EventName == "begin":
    #         self._argument_start_time = event.Timestamp
    #         self._waddle_count = 0
    #     elif event.EventName == "player_waddle":
    #         self._waddle_count += 1
    #     elif event.EventName == "enter_region":
    #         if event.event_data.get("region_name") == 'Mirror':
    #             Logger.Log(f"start time is {self._argument_start_time}")
    #             self._time = (event.Timestamp - self._argument_start_time).total_seconds()
    #             self._argument_start_time = None
    #         return
    #     self._prev_timestamp = event.Timestamp
    
    # def _extractFromFeatureData(self, feature:FeatureData):
    #     return

    # def _getFeatureValues(self) -> List[Any]:
    #     self._waddle_detector_dict['waddle_count']=self._waddle_count
    #     self._waddle_detector_dict['enter_duration'] = timedelta(seconds=self._time)
    #     return [self._waddle_detector_dict]

    