from typing import Any, List, Optional
# Import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.games.AQUALAB.features.PerJobFeature import PerJobFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

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
        if event.EventName == "recommended_job":
            self._received_recommendation = True
            self._waiting_for_switch = True
            self._followed_advice = False 

        elif event.EventName == "switch_job" and self._waiting_for_switch:
            prev_job_name = event.EventData.get("prev_job_name")
            if prev_job_name and self._job_map.get(prev_job_name) == self.CountIndex:
                self._followed_advice = True
                self._waiting_for_switch = False
   
    def _updateFromFeatureData(self, feature: FeatureData):
        return
    
    def _getFeatureValues(self) -> List[Any]:
        return [self._followed_advice]
    
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"


