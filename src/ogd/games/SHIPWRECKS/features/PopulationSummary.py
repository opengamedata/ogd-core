from collections import defaultdict
from typing import Any, Dict, List, Union
from unicodedata import numeric

from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class PopulationSummary(SessionFeature):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._session_completions = defaultdict(list)
        self._session_times = []

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["JobsCompleted", "SessionDuration"]

    def _updateFromEvent(self, event: Event) -> None:
        return

    def _updateFromFeatureData(self, feature:FeatureData):
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
