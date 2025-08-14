from collections import defaultdict
from datetime import timedelta
from typing import Any, Dict, List

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature

class PopulationSummary(SessionFeature):

    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self._user_sessions = defaultdict(set)
        self._user_counties_unlocked = defaultdict(int)
        self._user_active_times = defaultdict(list)

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["CountyUnlockCount", "ActiveTime", "NumberOfSessionsPerPlayer", "GameCompletionStatus"]

    def _updateFromEvent(self, event: Event) -> None:
        return

    def _updateFromFeature(self, feature: Feature):
        player_id = feature.PlayerID

        print(f"Processing feature: {feature}")
        
        if feature.ExportMode == ExtractionMode.PLAYER:
            if feature.FeatureType == "CountyUnlockCount":
                self._user_counties_unlocked[player_id] = feature.Values[0]
                
            elif feature.FeatureType == "ActiveTime":
                active_time = feature.Values[0]
                if isinstance(active_time, timedelta):
                    self._user_active_times[player_id].append(active_time.total_seconds())
                elif isinstance(active_time, str) and active_time == "No events":
                    pass
                else:
                    raise ValueError(f"PopulationSummary got {feature.Name} feature with value {active_time} of non-timedelta type {type(active_time)} in the {feature.FeatureNames[0]} column!")
                    
            elif feature.FeatureType == "GameCompletionStatus":
                if feature.Values[0] == 'WIN':
                    self._user_counties_unlocked[player_id] += 1
                    
        elif feature.ExportMode == ExtractionMode.SESSION:
            if feature.FeatureType == "NumberOfSessionsPerPlayer":
                self._user_sessions[player_id].add(feature.SessionID)

    def _getFeatureValues(self) -> List[Any]:
        num_sessions = [len(self._user_sessions[user]) for user in self._user_sessions]
        
        num_counties_unlocked = [
            self._user_counties_unlocked[user] 
            for user in self._user_counties_unlocked
        ]
        
        active_times = []
        for user in self._user_active_times:
            for time_seconds in self._user_active_times[user]:
                if isinstance(time_seconds, (int, float)):
                    active_times.append(time_seconds)

        summary = {
            "avg_session_count": 0,
            "avg_counties_unlocked": 0,
            "avg_active_time": 0
        }

        if len(num_sessions) > 0:
            summary["avg_session_count"] = sum(num_sessions) / len(num_sessions)

        if len(num_counties_unlocked) > 0:
            summary["avg_counties_unlocked"] = sum(num_counties_unlocked) / len(num_counties_unlocked)

        if len(active_times) > 0:
            summary["avg_active_time"] = sum(active_times) / len(active_times)

        return [summary]

    # *** Optionally override public functions. ***

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        """List of ExtractionMode supported by the Feature.

        Overridden from base Feature version.
        A PopulationSummary is only used at population level.
        :return: List of supported extraction modes
        :rtype: List[ExtractionMode]
        """
        return [ExtractionMode.POPULATION]
