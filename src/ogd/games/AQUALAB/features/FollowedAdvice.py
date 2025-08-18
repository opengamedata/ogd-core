from typing import Any, List, Optional
# Import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.games.AQUALAB.features.PerJobFeature import PerJobFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature

class FollowedAdvice(PerJobFeature):
    def __init__(self, params: GeneratorParameters, job_map: dict):
        super().__init__(params=params, job_map=job_map)
        self._followed_advice = None
        self._received_recommendation = False
        self._waiting_for_switch = False
    
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["all_events"]
    
    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []
    
    def _updateFromEvent(self, event: Event) -> None:
        player_actions = ["receive_fact", "receive_entity", "complete_job", "complete_task", "begin_dive", "begin_model", "begin_simulation", "add_environment", "remove_environment", "add_critter", "remove_critter", "begin_experiment", "begin_argument"]

        if event.EventName == "recommended_job":
            attempted_job_name = event.EventData.get("attempted_job_name", None)
            if attempted_job_name and attempted_job_name == self.TargetJobName:
                self._received_recommendation = True
                self._waiting_for_switch = True
                self._followed_advice = False 
        
        if self._waiting_for_switch and event.EventName in player_actions:
                    self._waiting_for_switch = False
        elif event.EventName == "switch_job" and self._waiting_for_switch:
            pre_job_name = event.EventData.get("prev_job_name", None)
            # if pre_job_name in self._job_map and self._job_map.get(pre_job_name) == self.CountIndex:
            if pre_job_name == self.TargetJobName:
                self._followed_advice = True
                self._waiting_for_switch = False
   
    def _updateFromFeature(self, feature: Feature):
        return
    
    def _getFeatureValues(self) -> List[Any]:
        return [self._followed_advice]
    
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
