from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
import time

class PersistenceTime(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.fail_times: List[int] = []
        self.current_start_time: Optional[int] = None
        self.total_seconds_list: List[int] = []

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["lose_game", "win_game", "pause_game"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        event_type = event.EventName

        if event_type == "lose_game":
            if self.current_start_time is not None:
                elapsed_time = int(time.time()) - self.current_start_time
                self.total_seconds_list.append(elapsed_time)
            self.current_start_time = int(time.time())
        elif event_type == "win_game" and self.current_start_time is not None:
            elapsed_time = int(time.time()) - self.current_start_time
            self.total_seconds_list.append(elapsed_time)
            self.current_start_time = None
        elif event_type == "pause_game":
            if self.current_start_time is not None:
                elapsed_time = int(time.time()) - self.current_start_time
                self.total_seconds_list.append(elapsed_time)
                self.current_start_time = None

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        total_time = sum(self.total_seconds_list)
        return [total_time]

    # Subfeature breakdown
    def _getSubfeatureValues(self) -> Dict[str, Any]:
        breakdown = sum(self.total_seconds_list)
        return {"Breakdown": breakdown, "TotalTimeList": self.total_seconds_list}

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
