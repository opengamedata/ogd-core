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

class JobArgumentationRejects(PerJobFeature):
    def __init__(self, params:GeneratorParameters, job_map:dict):
        super().__init__(params=params, job_map=job_map)
        self._inside_argument = False
        self._fact_rejected_inside_argument = 0
        self._fact_rejected_total = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["begin_argument", "fact_rejected", "leave_argument", "complete_argument"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if event.EventName == "begin_argument":
            self._inside_argument = True
        elif event.EventName in ("leave_argument", "complete_argument"):
            self._inside_argument = False
        elif event.EventName == "fact_rejected":
            self._fact_rejected_total += 1
            if self._inside_argument:
                self._fact_rejected_inside_argument += 1

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if self._fact_rejected_total != self._fact_rejected_inside_argument:
            _msg = "\n".join([f"JobArgumentationRejects Mismatch: "
                f"total fact_rejected={self._fact_rejected_total}, "
                f"inside_argument fact_rejected={self._fact_rejected_inside_argument}"])
            Logger.Log(message=_msg, level=logging.WARNING)
        return [self._fact_rejected_inside_argument]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "3"
