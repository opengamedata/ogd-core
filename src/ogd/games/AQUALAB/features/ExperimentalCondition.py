from typing import Any, List, Optional
# Import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature

class ExperimentalCondition(Feature):
    def __init__(self, params: GeneratorParameters, job_map: dict):
        super().__init__(params=params)
        self.app_branch = None  

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["all_events"]  

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        if self.app_branch is None:
            self.app_branch = event.AppBranch  

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self.app_branch] 

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
