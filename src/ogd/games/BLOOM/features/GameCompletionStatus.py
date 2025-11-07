# import libraries
from typing import Any, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature

class GameCompletionStatus(Extractor):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.status: Optional[str] = "IN_PROGRESS"

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["win_game", "lose_game"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        if event.EventName == "win_game":
            self.status = "WIN"
        elif event.EventName == "lose_game":
            self.status = "LOSS"

    def _updateFromFeature(self, feature: Feature):
        pass

    def _getFeatureValues(self) -> List[Any]:
        return [self.status]
