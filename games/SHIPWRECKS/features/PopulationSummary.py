from collections import defaultdict
from typing import Any, Dict, List, Union
from unicodedata import numeric

from schemas.FeatureData import FeatureData
from extractors.features.SessionFeature import SessionFeature
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event

class PopulationSummary(SessionFeature):

    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._session_completions = defaultdict(list)
        self._session_times = []

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["JobsCompleted", "SessionDuration"]

    def _extractFromEvent(self, event: Event) -> None:
        return

    def _extractFromFeatureData(self, feature:FeatureData):
        if feature.FeatureType == "JobsCompleted":
            self._session_completions[feature.SessionID] = feature.FeatureValues[0]
        elif feature.FeatureType == "SessionDuration":
            self._session_times.append(feature.FeatureValues[0])

    def _getFeatureValues(self) -> List[Any]:
        num_completions = [len(self._session_completions[session]) for session in self._session_completions]

        summary : Dict[str, Union[float, int]] = {
            "avg_session_count": 1,
            "avg_jobs_completed": 0,
            "avg_session_time": 0
        }

        if len(num_completions) > 0:
            summary["avg_jobs_completed"] = sum(num_completions) / len(num_completions)

        if len(self._session_times) > 0:
            summary["avg_session_time"] = sum(self._session_times) / len(self._session_times)

        return [summary]

    # *** Optionally override public functions. ***
