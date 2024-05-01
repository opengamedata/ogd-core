from typing import Any, List
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData

class PlayMode(SessionFeature):

    def __init__(self, params: GeneratorParameters):
        self.play_mode = None
        super().__init__(params=params)

    @classmethod
    def _getEventDependencies(cls, mode: ExtractionMode) -> List[str]:
        return ["game_start"]

    @classmethod
    def _getFeatureDependencies(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event: Event) -> None:
        if event.EventName == "game_start":
            mode = event.EventData.get("mode")
            if mode:
                self.play_mode = mode

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self.play_mode]
