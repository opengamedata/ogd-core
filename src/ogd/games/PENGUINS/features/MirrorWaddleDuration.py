# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from datetime import datetime, timedelta
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.generators.extractors.SessionFeature import SessionFeature

class MirrorWaddleDuration(SessionFeature):
    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._session_id = None
        self._argument_start_time : Optional[datetime] = None
        self._prev_timestamp = None
        self._time = 0
        self._waddle_count = 0


    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return [ "player_waddle"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:


        if event.SessionID != self._session_id:
            self._session_id = event.SessionID
            # if we jumped to a new session, we only want to count time up to last event, not the time between sessions.
            if self._argument_start_time and self._prev_timestamp:
                self._time += (self._prev_timestamp - self._argument_start_time).total_seconds()
                self._argument_start_time = event.Timestamp
        


        elif self._argument_start_time is not None:
            if event.event_name == "player_waddle":
                self._waddle_count += 1
                self._time = (event.Timestamp - self._argument_start_time).total_seconds()
                self._argument_start_time = None
                return
            
        self._prev_timestamp = event.Timestamp
    
    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [{"waddle":self._waddle_count, "duration": self._time}]

    
    # def __init__(self, params:GeneratorParameters):
    #     super().__init__(params=params)
    #     self._session_id = None
    #     self._argument_start_time : Optional[datetime] = None
    #     self._prev_timestamp = None
    #     self._time = 0
    #     self._waddle_count = 0
    #     self._waddle_detector_dict = dict()

    # # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    # @classmethod
    # def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
    #     return ["enter_region", "player_waddle",'begin']

    # @classmethod
    # def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
    #     return []

    # def _updateFromEvent(self, event:Event) -> None:
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
    
    # def _updateFromFeatureData(self, feature:FeatureData):
    #     return

    # def _getFeatureValues(self) -> List[Any]:
    #     self._waddle_detector_dict['waddle_count']=self._waddle_count
    #     self._waddle_detector_dict['enter_duration'] = timedelta(seconds=self._time)
    #     return [self._waddle_detector_dict]

    