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
        self._difficulties = self._diff_map[self.CountIndex]

        ret_val : bool = False

        # print(self._difficulties)
        # print(self._difficulty_type)
        if self._difficulties[self._difficulty_type] is not None:
            if self._difficulties[self._difficulty_type] == self.CountIndex:
                ret_val = True
                #print("found!")
        else:
            #pass
            Logger.Log(f"Got invalid job_name data in {type(self).__name__}", logging.WARNING)

        return ret_val

    # *** Optionally override public functions. ***

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "0"
