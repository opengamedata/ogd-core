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


class JobInterventionFails(PerJobFeature):
    """Feature to count the number of times a player attempted a intervention model in a job, but was unsuccessful.

    We assume that any attempt to manipulate the model (identified by a model_intervene_update event) constituted an intervention modeling attempt.
    If the player subsequently ends modeling without a "completed" event for the intervention model, it is considered a failure.
    """

    def __init__(self, params:GeneratorParameters, job_map:dict):
        super().__init__(params=params, job_map=job_map)
        self._started    : bool = False
        self._completed  : bool = False
        self._fail_count : int = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["model_intervene_update", "model_intervene_completed", "model_end"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        match event.EventName:
            case "model_intervene_update":
                self._started = True
            case "model_intervene_completed":
                self._completed = True
            case "model_end":
                if self._started and not self._completed:
                    self._fail_count += 1
                self._started = False
                self._completed = False
    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        # if(self._success_count > self._leave_count):
        #     return [0]
        # else:
        # NOTE : after complete, player always has a 'leave' after they get dumped into no-active-job. So no-active-job will have many argumentation 'fails'
        return [self._fail_count]
        


    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return
