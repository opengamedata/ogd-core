# import libraries
from typing import Any, List
from schemas import Event
from extractors.features.PerLevelFeature import PerLevelFeature
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData

class StoryScore(PerLevelFeature):
    def __init__(self, params: ExtractorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._story_score = 0

    @classmethod
    def _getEventDependencies(cls, mode: ExtractionMode) -> List[str]:
        return ["display_feedback_dialog"]

    @classmethod
    def _getFeatureDependencies(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event: Event) -> None:
        if event.name == "display_feedback_dialog":
            self._story_score = event.data["story_score"]

    def _extractFromFeatureData(self, feature: FeatureData):
        return []

    def _getFeatureValues(self) -> List[Any]:
        return [self._story_score]

    def Subfeatures(self) -> List[str]:
        return []
