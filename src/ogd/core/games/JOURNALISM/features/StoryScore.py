# import libraries
from typing import Any, List
from ogd.core.schemas import Event
from ogd.core.extractors.features.PerLevelFeature import PerLevelFeature
from ogd.core.extractors.Extractor import ExtractorParameters
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData

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
        if event.EventName == "display_feedback_dialog":
            self._story_score = event.EventData["story_score"]

    def _extractFromFeatureData(self, feature: FeatureData):
        return []

    def _getFeatureValues(self) -> List[Any]:
        return [self._story_score]

    def Subfeatures(self) -> List[str]:
        return []
