# import libraries
import logging
from typing import Any, List, Optional
# import locals
from utils import Logger
from games.AQUALAB.features.PerJobFeature import PerJobFeature
from schemas.FeatureData import FeatureData
from schemas.Event import Event

class JobHelpCount(PerJobFeature):

    def __init__(self, name:str, description:str, job_num:int, job_map:dict):
        self._job_map = job_map
        super().__init__(name=name, description=description, job_num=job_num, job_map=job_map)
        self._count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["ask_for_help"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._count += 1

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***
    def MinVersion(self) -> Optional[str]:
        return "1"
