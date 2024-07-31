"""# import libraries
from datetime import timedelta
from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

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
"""

from typing import Any, Dict, List, Optional
from datetime import timedelta
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class AverageActiveTime(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.active_time_per_session: Dict[str, timedelta] = {}
        self.session_start_time: Dict[str, Optional[Event]] = {}

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["session_start", "pause_game", "unpause_game"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        session_id = event.SessionID
        if event.EventName == "session_start":
            self.session_start_time[session_id] = event
        elif event.EventName == "pause_game":
            start_time = self.session_start_time.get(session_id)
            if start_time:
                active_time = event.Timestamp - start_time.Timestamp
                self.active_time_per_session[session_id] = self.active_time_per_session.get(session_id, timedelta()) + active_time
        elif event.EventName == "unpause_game":
            self.session_start_time[session_id] = event

    def _updateFromFeatureData(self, feature: FeatureData):
        pass

    def _getFeatureValues(self) -> List[Any]:
        total_active_time = sum(self.active_time_per_session.values(), timedelta())
        session_count = len(self.active_time_per_session)
        if session_count == 0:
            return [timedelta()]  # Return zero if no sessions
        average_active_time = total_active_time / session_count
        return [average_active_time]

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
