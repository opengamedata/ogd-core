# import libraries
import logging
from datetime import datetime, timedelta
from typing import Any, List, Union
# import locals
import utils
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class JobArgumentationTime(Feature):

    def __init__(self, name:str, description:str, job_num:int, job_map:dict):
        self._job_map = job_map
        super().__init__(name=name, description=description, count_index=job_num)
        self._argument_start_time : Union[datetime, None] = None
        self._time = timedelta(0)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["begin_argument", "room_changed"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if self._validate_job(event.event_data["job_name"]):
            if event.event_name == "begin_argument":
                self._argument_start_time = event.timestamp
            elif event.event_name == "room_changed" and self._argument_start_time is not None:
                self._time += event.timestamp - self._argument_start_time
                self._argument_start_time = None
    
    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._time]

    # *** Optionally override public functions. ***
    def MinVersion(self) -> Union[str,None]:
        return "1"

    # *** Other local functions
    def _validate_job(self, job_data):
        ret_val : bool = False
        if job_data['string_value'] is not None:
            if self._job_map[job_data['string_value']] == self._count_index:
                ret_val = True
        else:
            utils.Logger.Log(f"Got invalid job_name data in JobArgumentationTime", logging.WARNING)
        return ret_val
