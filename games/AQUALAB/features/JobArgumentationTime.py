# import libraries
import logging
from datetime import datetime, timedelta
from typing import Any, List, Optional
# import locals
from utils import Logger
from features.Feature import Feature
from schemas.FeatureData import FeatureData
from schemas.Event import Event

class JobArgumentationTime(Feature):

    def __init__(self, name:str, description:str, job_num:int, job_map:dict):
        self._job_map = job_map
        super().__init__(name=name, description=description, count_index=job_num)
        self._session_id = None
        self._argument_start_time : Optional[datetime] = None
        self._prev_timestamp = None
        self._time = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["begin_argument", "room_changed"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.SessionID != self._session_id:
            self._session_id = event.SessionID
            
            if self._argument_start_time:
                self._time += (self._prev_timestamp - self._argument_start_time).total_seconds()
                self._argument_start_time = event.Timestamp

        if self._validate_job(event.EventData["job_name"]):
            if event.EventName == "begin_argument":
                self._argument_start_time = event.Timestamp
            elif event.EventName == "room_changed" and self._argument_start_time is not None:
                self._time += (event.Timestamp - self._argument_start_time).total_seconds()
                self._argument_start_time = None
        
        self._prev_timestamp = event.Timestamp
    
    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [timedelta(seconds=self._time)]

    # *** Optionally override public functions. ***
    def MinVersion(self) -> Optional[str]:
        return "1"

    # *** Other local functions
    def _validate_job(self, job_data):
        ret_val : bool = False
        if job_data['string_value'] is not None:
            if job_data['string_value'] in self._job_map and self._job_map[job_data['string_value']] == self._count_index:
                ret_val = True
        else:
            Logger.Log(f"Got invalid job_name data in JobArgumentationTime", logging.WARNING)
        return ret_val
