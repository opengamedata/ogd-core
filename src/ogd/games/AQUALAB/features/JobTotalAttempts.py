# import libraries
from typing import Any, List, Optional
# import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.games.AQUALAB.features.PerJobFeature import PerJobFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature

class JobTotalAttempts(PerJobFeature):
    _checked_alive = False
    def __init__(self, params:GeneratorParameters, job_map:dict):
        super().__init__(params=params, job_map=job_map)
        self._count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["JobAttempted"]

    def _updateFromEvent(self, event:Event) -> None:
        return

    def _updateFromFeature(self, feature:Feature):
        if feature.ExportMode == ExtractionMode.PLAYER and feature.CountIndex == self.CountIndex:
            if not self._checked_alive:
                Logger.Log(f"JobTotalAttempts for job {self.CountIndex} got a feature at player level with same count index")
                self._checked_alive = True
            if feature.Values[0] == True:
                self._count += 1

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***
    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.POPULATION]

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"