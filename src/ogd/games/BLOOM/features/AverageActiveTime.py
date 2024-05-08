# import libraries
from datetime import timedelta
from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData

class AverageActiveTime(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.active_time_per_session: Dict[str, timedelta] = {} 
        self.session_count: Dict[str, int] = {}  

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["session_start", "pause_game", "unpause_game"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["ActiveTime", "NumberOfSessionsPerPlayer"]  

    def _updateFromEvent(self, event: Event) -> None:
        if event.EventName == "session_start":
            player_id = event.PlayerID
            self.session_count[player_id] = self.session_count.get(player_id, 0) + 1
        elif event.EventName == "pause_game":
            player_id = event.PlayerID
            self.active_time_per_session[player_id] = self.active_time_per_session.get(player_id, timedelta())
            self.active_time_per_session[player_id] -= event.Timestamp
        elif event.EventName == "unpause_game":
            player_id = event.PlayerID
            self.active_time_per_session[player_id] = self.active_time_per_session.get(player_id, timedelta())
            self.active_time_per_session[player_id] += event.Timestamp

    def _updateFromFeatureData(self, feature: FeatureData):
        if feature.Name == "ActiveTime":
            self.active_time_per_session = feature.Value 
        elif feature.Name == "NumberOfSessionsPerPlayer":
            self.session_count = feature.Value 

    def _getFeatureValues(self) -> List[Any]:
        average_active_time = {}
        for player_id, active_time in self.active_time_per_session.items():
            session_count = self.session_count.get(player_id, 0)
            if session_count != 0:
                average_active_time[player_id] = active_time / session_count
        return [average_active_time]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
