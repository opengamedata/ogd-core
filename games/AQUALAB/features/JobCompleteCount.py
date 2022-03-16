import logging
from typing import Any, List, Union

import utils
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class JobCompleteCount(Feature):

    def __init__(self, name:str, description:str, job_num:int, job_map:dict):
        self._job_map = job_map
        super().__init__(name=name, description=description, count_index=job_num)
        self._completed = 0

    def GetEventDependencies(self) -> List[str]:
        return ["complete_job"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        return [self._completed]

    def MinVersion(self) -> Union[str,None]:
        return "1"

    def _extractFromEvent(self, event:Event) -> None:
        if "job_name" in event.event_data.keys():
            if self._validate_job(event.event_data['job_name']):
                self._completed += 1
        else:
            raise ValueError(f"job_name not found in keys of event type {event.event_name}, the keys were:\n{event.event_data.keys()}")

    def _validate_job(self, job_data):
        ret_val : bool = False
        if job_data['string_value'] is not None:
            if self._job_map[job_data['string_value']] == self._count_index:
                ret_val = True
        else:
            utils.Logger.Log(f"Got invalid job_name data in JobCompleteCount", logging.WARNING)
        return ret_val

    def _extractFromFeatureData(self, feature: FeatureData):
        return
