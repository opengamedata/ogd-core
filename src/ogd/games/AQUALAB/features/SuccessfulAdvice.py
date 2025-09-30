import logging
from typing import Any, List, Optional
# Import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.games.AQUALAB.features.PerJobFeature import PerJobFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

class SuccessfulAdvice(PerJobFeature):
    def __init__(self, params: GeneratorParameters, job_map: dict):
        super().__init__(params=params, job_map=job_map)
        self._successful_advice = None
        self._received_recommendation = False
        self._waiting_to_leave = False
        self._waiting_to_return = False

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["all_events"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        player_actions = ["receive_fact", "receive_entity", "complete_job", "complete_task", "begin_dive", "begin_model", "begin_simulation", "add_environment", "remove_environment", "add_critter", "remove_critter", "begin_experiment", "begin_argument"]

        # Anytime we get a recommendation, we start waiting to leave
        if event.EventName == "recommended_job":
            attempted_job_name = event.EventData.get("attempted_job_name", None)
            if self._received_recommendation:
                Logger.Log(f"Received multiple recommendations for the same job ({attempted_job_name})!", logging.DEBUG)
            if attempted_job_name in self._job_map and attempted_job_name == self.TargetJobName:
                self._received_recommendation = True
                self._waiting_to_leave = True
                self._successful_advice = False
        # If we previously received a recommendation, we want to know when we switch away and back.
        elif event.EventName == "switch_job" and self._received_recommendation:
            prev_job_name = event.EventData.get("prev_job_name")
            new_job_name  = event.GameState.get("job_name")
            if prev_job_name == self.TargetJobName and new_job_name != self.TargetJobName:
                self._waiting_to_leave = False 
                self._waiting_to_return = True
            elif prev_job_name != self.TargetJobName and new_job_name == self.TargetJobName:
                self._waiting_to_return = False
            else:
                Logger.Log(f"Got unexpected job switch: switch from {prev_job_name} to {new_job_name} was sent to SuccessfulAdvice feature for {self.TargetJobName}!", logging.WARNING)
        # If we're waiting to switch away, watch for player actions
        elif event.EventName in player_actions and self._waiting_to_leave:
            self._successful_advice = False
        # If we previously received a recommendation, and aren't waiting on switching away and back, then we've had successful advice-following behavior.
        elif event.EventName == "complete_job" and self._received_recommendation and not self._waiting_to_leave and not self._waiting_to_return:
            self._successful_advice = True

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._successful_advice]

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        """List of ExtractionMode supported by the Feature.

        Overridden from Extractor's version of the function, only makes the Feature-related modes supported.
        :return: _description_
        :rtype: List[ExtractionMode]
        """
        return [ExtractionMode.PLAYER, ExtractionMode.SESSION]
