# import libraries
import logging
from typing import Optional
# import locals
from utils.Logger import Logger
from extractors.Extractor import ExtractorParameters
from extractors.features.PerCountFeature import PerCountFeature
from schemas.Event import Event

class PerDifficultyFeature(PerCountFeature):
    def __init__(self, params:ExtractorParameters, diff_map: dict, difficulty_type):
        super().__init__(params=params)
        self._difficulty_type = difficulty_type
        self._diff_map = diff_map

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _validateEventCountIndex(self, event:Event):
        ret_val : bool = False

        _current_job = event.EventData.get('job_name', "UNKNOWN JOB")['string_value']
       # print(_current_job)
        if self._diff_map[_current_job][self._difficulty_type] == self.CountIndex:
            ret_val = True
        
        return ret_val

    # *** Optionally override public functions. ***

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "3"
