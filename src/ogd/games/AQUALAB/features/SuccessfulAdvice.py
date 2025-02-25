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
        self._switched_away = False
        self._switched_back = False
    
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["all_events"]
    
    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []
    
    def _updateFromEvent(self, event: Event) -> None:
        if event.EventName == "recommended_job":
            self._received_recommendation = True
            self._successful_advice = False
        
        elif event.EventName == "switch_job" and self._received_recommendation:
            job_name = event.GameState.get("job_name")
            if job_name != self.CountIndex:
                self._switched_away = True
            elif self._switched_away:
                self._switched_back = True
        
        elif event.EventName == "complete_job" and self._switched_away and self._switched_back:
            self._successful_advice = True
        
    def _updateFromFeatureData(self, feature: FeatureData):
        return
    
    def _getFeatureValues(self) -> List[Any]:
        return [self._successful_advice]
    
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
