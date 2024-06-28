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

class PlayerInactiveAvgDuration(SessionFeature):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._session_id = None
        self._argument_start_time : Optional[datetime] = None
        self._prev_timestamp = None
        self._time = 0
        self._inactive_count = 0
        self._evt_name = None
        self._inactive_time_lst = list()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["all_events"]

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
        if event.EventName != "viewport_data":
            if  self._argument_start_time is None :
                self._evt_name = event.EventName
                self._argument_start_time = event.Timestamp
            else:
                self._time = (event.Timestamp - self._argument_start_time).total_seconds()
                self._inactive_time_lst.append(self._time)
                self._argument_start_time = None
        self._prev_timestamp = event.Timestamp
    
    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        Logger.Log(f"sum is {sum(self._inactive_time_lst)}")
        Logger.Log(f"length is {len(self._inactive_time_lst)}")
        if (len(self._inactive_time_lst) != 0):
            return [sum(self._inactive_time_lst)/len(self._inactive_time_lst)]
        else:
            return [None]

    