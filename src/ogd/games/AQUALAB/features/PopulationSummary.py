from collections import defaultdict
from datetime import timedelta
from typing import Any, Dict, List

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class PopulationSummary(SessionFeature):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._user_sessions = defaultdict(list)
        self._user_completions = defaultdict(list)
        self._user_session_times = defaultdict(list)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["JobsCompleted", "SessionID", "SessionDuration"]

    def _updateFromEvent(self, event: Event) -> None:
        return

    def _updateFromFeatureData(self, feature:FeatureData):
        if feature.FeatureType == "JobsCompleted":
            self._user_completions[feature.PlayerID].append(feature.FeatureValues[0])
        elif feature.FeatureType == "SessionID" and feature.SessionID not in self._user_sessions[feature.PlayerID]:
            self._user_sessions[feature.PlayerID].append(feature.SessionID)
        elif feature.FeatureType == "SessionDuration":
            self._user_session_times[feature.PlayerID].append(feature.FeatureValues[0])

    def _getFeatureValues(self) -> List[Any]:
        num_sessions = [len(self._user_sessions[user]) for user in self._user_sessions]
        num_completions = [len(self._user_completions[user]) for user in self._user_completions]
        session_times : List[timedelta] = []

        for user in self._user_session_times:
            for time in self._user_session_times[user]:
                if type(time) == str and time == "No events":
                    pass
                else:
                    session_times.append(time)

        summary : Dict[str, float]= {
            "avg_session_count": 0,
            "avg_jobs_completed": 0,
            "avg_session_time": 0
        }

        if len(num_sessions) > 0:
            summary["avg_session_count"] = int(sum(num_sessions) / len(num_sessions))

        if len(num_completions) > 0:
            summary["avg_jobs_completed"] = int(sum(num_completions) / len(num_completions))

        if len(session_times) > 0:
            summary["avg_session_time"] = PopulationSummary._timesum(session_times) / len(session_times)

        return [summary]

    # *** Optionally override public functions. ***

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        """List of ExtractionMode supported by the Feature.

        Overridden from base Feature version.
        A PlayerSummary is only used at player and population levels; not concerned with session-level.
        :return: _description_
        :rtype: List[ExtractionMode]
        """
        return [ExtractionMode.POPULATION]

    # *** Private Functions ***

    @staticmethod
    def _timesum(times:List[timedelta]):
        ret_val = timedelta(0)
        for time in times:
            ret_val += time
        return ret_val.total_seconds()
