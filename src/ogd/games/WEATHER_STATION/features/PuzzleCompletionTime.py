# import libraries
from datetime import datetime, timedelta
from typing import Any, Final, List, Optional
# import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event, EventSource
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

class PuzzleCompletionTime(Feature):
    
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.current_session = None
        self.session_count = 0
        self.puzzle_start_times = {"BATTERY": None, "THERMOMETER": None, "DATA_LOGGER": None, "TURBINE": None, "SOLAR": None}
        self.puzzle_completion_durations = {"BATTERY": 0, "THERMOMETER": 0, "DATA_LOGGER": 0, "TURBINE": 0, "SOLAR": 0}

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["start_puzzle", "complete_puzzle"]

    def Subfeatures(self) -> List[str]:
        return ["battery", "thermometer", "data_logger", "turbine", "solar"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        session_id = event.SessionID
        if session_id != self.current_session:
            self.current_session = session_id
            self.session_count += 1
            
        puzzle = event.EventData.get("puzzle", None)

        if event.EventName == "start_puzzle":
            self.puzzle_start_times[puzzle] = event.GameState.get("seconds_from_launch", None)
        elif event.EventName == "complete_puzzle" and self.puzzle_start_times[puzzle] is not None:
            self.puzzle_completion_durations[puzzle] += event.GameState.get("seconds_from_launch", None) - self.puzzle_start_times[puzzle]
            self.puzzle_start_times[puzzle] = None

    def _updateFromFeatureData(self, feature: FeatureData):
        pass

    def _getFeatureValues(self) -> List[Any]:
        return [
            "",
            self.puzzle_completion_durations["BATTERY"],
            self.puzzle_completion_durations["THERMOMETER"],
            self.puzzle_completion_durations["DATA_LOGGER"],
            self.puzzle_completion_durations["TURBINE"],
            self.puzzle_completion_durations["SOLAR"]
        ]

    # *** Optionally override public functions ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
