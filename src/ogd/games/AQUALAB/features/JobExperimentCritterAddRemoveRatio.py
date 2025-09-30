# import libraries
import logging
from typing import Any, List, Optional
# import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.games.AQUALAB.features.PerJobFeature import PerJobFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData


"""
n_critter_remove/(n_critter_add + n_critter_remove)
"""
class JobExperimentCritterAddRemoveRatio(PerJobFeature):

    def __init__(self, params:GeneratorParameters, job_map:dict):
        super().__init__(params=params, job_map=job_map)
        self._n_remove = 0
        self._n_add = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["add_critter", "remove_critter"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if(event.EventName == "add_critter"):
            self._n_add += 1
        if(event.EventName == "remove_critter"):
            self._n_remove += 1
        


    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if(self._n_remove >= 1 and self._n_add >= 1):
            return [abs(self._n_remove/(self._n_remove + self._n_add))]
        elif(self._n_add < 1 and self._n_remove != 0):
            return [1]
        else:
            return [0]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return
