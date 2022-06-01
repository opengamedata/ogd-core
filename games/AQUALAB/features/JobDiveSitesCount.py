# import libraries
import logging
from typing import Any, List, Optional
# import locals
from utils import Logger
from features.Feature import Feature
from schemas.FeatureData import FeatureData
from schemas.Event import Event

class JobDiveSitesCount(Feature):
    
    def __init__(self, name:str, description:str, job_num:int, job_map:dict):
        self._job_map = job_map
        super().__init__(name=name, description=description, count_index=job_num)
        self._count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["begin_dive"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if self._validate_job(event.EventData['job_name']):
            self._count += 1

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***
    def MinVersion(self) -> Optional[str]:
        return "1"

    # *** Other local functions
    def _validate_job(self, job_data):
        ret_val : bool = False
        if job_data['string_value'] is not None:
            if job_data['string_value'] in self._job_map and self._job_map[job_data['string_value']] == self.CountIndex:
                ret_val = True
        else:
            Logger.Log(f"Got invalid job_name data in JobDiveSitesCount", logging.WARNING)
        return ret_val
