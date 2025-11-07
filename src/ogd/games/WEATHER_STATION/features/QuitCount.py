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
from .utils import _getIndexNameFromEvent

class QuitCount(Feature):
    
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.puzzle_quit_counts = {"BATTERY": 0, "THERMOMETER": 0, "DATA_LOGGER": 0, "TURBINE": 0, "SOLAR": 0}

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
        puzzle = event.EventData.get("puzzle", None)
        if puzzle is None:
            return

        if event.EventName == "start_puzzle":
            self.puzzle_quit_counts[puzzle] += 1
        elif event.EventName == "complete_puzzle":
            self.puzzle_quit_counts[puzzle] -= 1

    def _updateFromFeatureData(self, feature: FeatureData):
        pass

    def _getFeatureValues(self) -> List[Any]:
        return [
            "",
            self.puzzle_quit_counts["BATTERY"],
            self.puzzle_quit_counts["THERMOMETER"],
            self.puzzle_quit_counts["DATA_LOGGER"],
            self.puzzle_quit_counts["TURBINE"],
            self.puzzle_quit_counts["SOLAR"]
        ]

    # *** Optionally override public functions ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
