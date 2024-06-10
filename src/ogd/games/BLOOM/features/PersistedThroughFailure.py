from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData

class PersistedThroughFailure(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.failure_count: int = 0
        self.win_after_failure: bool = False

    # Implement abstract functions
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["lose_game", "win_game"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        event_type = event.EventType
        if event_type == "lose_game":
            self.failure_count += 1
        elif event_type == "win_game" and self.failure_count > 0:
            self.win_after_failure = True

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if self.failure_count > 0:
            return [self.win_after_failure]
        else:
            return [None]

    # Optionally override public functions
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
