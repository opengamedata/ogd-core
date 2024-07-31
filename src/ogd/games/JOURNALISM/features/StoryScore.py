# import libraries
from typing import Any, List
from ogd.core.models import Event
from ogd.core.generators.extractors.PerLevelFeature import PerLevelFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData


class StoryScore(PerLevelFeature):
    def __init__(self, params: GeneratorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._story_score = 0

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["display_feedback_dialog"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        if event.EventName == "display_feedback_dialog":
            self._story_score = event.EventData["story_score"]

    def _updateFromFeatureData(self, feature: FeatureData):
        return []

    def _getFeatureValues(self) -> List[Any]:
        return [self._story_score]

    def Subfeatures(self) -> List[str]:
        return []
