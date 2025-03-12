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
            attempted_job_name = event.EventData.get("attempted_job_name", None)
            if attempted_job_name in self._job_map and attempted_job_name == self.TargetJobName:
                self._received_recommendation = True
                self._successful_advice = False

        elif event.EventName == "switch_job" and self._received_recommendation:
            prev_job_name = event.EventData.get("prev_job_name")
            new_job_name  = event.GameState.get("job_name")
            if prev_job_name == self.TargetJobName and new_job_name != self.TargetJobName:
                self._switched_away = True 
            elif prev_job_name != self.TargetJobName and new_job_name == self.TargetJobName:
                self._switched_back = True
            else:
                Logger.Log(f"Got unexpected job switch: switch from {prev_job_name} to {new_job_name} was sent to SuccessfulAdvice feature for {self.TargetJobName}!", logging.WARNING)

        elif event.EventName == "complete_job" and self._switched_away and self._switched_back:
            self._successful_advice = True

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._successful_advice]

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
