from typing import Any, List, Optional
# Import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

class PlayedNonexperimentalVersion(Feature):
    EXPERIMENTAL_BRANCHES = [
        "production-has-failure-prediction-original-job-graph",
        "production-no-failure-prediction-alt-job-graph",
        "production-no-failure-prediction-original-job-graph"
    ]
    def __init__(self, params: GeneratorParameters, job_map: dict):
        super().__init__(params=params)
        self.played_nonexperiment = False  

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["all_events"]  

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        if not self.played_nonexperiment:
            if event.AppBranch not in PlayedNonexperimentalVersion.EXPERIMENTAL_BRANCHES:
                self.played_nonexperiment = True

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self.played_nonexperiment] 

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
