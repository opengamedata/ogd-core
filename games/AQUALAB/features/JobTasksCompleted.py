import logging
from typing import Any, List, Union

import utils
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class JobTasksCompleted(Feature):
    
    def __init__(self, name:str, description:str, job_num:int, job_map:dict):
        self._job_map = job_map
        super().__init__(name=name, description=description, count_index=job_num)
        self._count = 0

    def GetEventDependencies(self) -> List[str]:
        return ["complete_task"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        return [self._count]

    def MinVersion(self) -> Union[str,None]:
        return "1"

    def _extractFromEvent(self, event:Event) -> None:
        if self._validate_job(event.event_data['job_name']):
            self._count += 1

    def _validate_job(self, job_data):
        ret_val : bool = False
        if job_data['string_value'] is not None:
            if self._job_map[job_data['string_value']] == self._count_index:
                ret_val = True
        else:
            utils.Logger.Log(f"Got invalid job_name data in JobTasksCompleted", logging.WARNING)
        return ret_val

    def _extractFromFeatureData(self, feature: FeatureData):
        return
