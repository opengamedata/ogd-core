# import libraries
import logging
from datetime import timedelta
from typing import Any, List, Optional
# import locals
from utils import Logger
from features.PerCountFeature import PerCountFeature
from schemas.FeatureData import FeatureData
from schemas.Event import Event

class PerJobFeature(PerCountFeature):
    def __init__(self, name:str, description:str, job_num:int, job_map:dict):
        super().__init__(name=name, description=description, count_index=job_num)
        self._job_map = job_map

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _validate_job(self, job_data):
        ret_val : bool = False
        if job_data['string_value'] is not None:
            if job_data['string_value'] in self._job_map and self._job_map[job_data['string_value']] == self.CountIndex:
                ret_val = True
        else:
            Logger.Log(f"Got invalid job_name data in JobCompletionTime", logging.WARNING)
        return ret_val

    # *** Optionally override public functions. ***

    def MinVersion(self) -> Optional[str]:
        return "1"
