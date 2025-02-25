# import libraries
import logging
from typing import Optional
# import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.common.models.Event import Event
from ogd.games.AQUALAB.AqualabLoader import METADATA

class PerJobFeature(PerCountFeature):
    def __init__(self, params:GeneratorParameters, job_map:dict):
        super().__init__(params=params,)
        self._job_map = job_map

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _validateEventCountIndex(self, event:Event):
        ret_val : bool = False

        job_name = event.GameState.get('job_name', event.EventData.get('job_name', "JOB NAME NOT FOUND"))
        if job_name is not None:
            if job_name in self._job_map and self._job_map[job_name] == self.CountIndex:
                ret_val = True
        else:
            self.WarningMessage(f"Got invalid job_name data in {type(self).__name__}")

        return ret_val

    # *** Optionally override public functions. ***

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"

    # *** Add Property ***
    
    @property
    def TargetJobName(self) -> str:
        ret_val = "NOT FOUND"

        if self.CountIndex == 0:
            ret_val = "no-active-job"
        else:
            job_list = METADATA.get("jobs", [])
            # we'll access CountIndex - 1, since index 0 is for no-active-job, so index 1 will be for 0th item in list of jobs.
            job_dict = job_list[self.CountIndex - 1] if len(job_list) >= self.CountIndex else {}
            ret_val = job_dict.get("id", "NOT FOUND")

        return ret_val
