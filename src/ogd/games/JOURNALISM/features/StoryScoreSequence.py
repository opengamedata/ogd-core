# import libraries
from typing import Any, List
from ogd.core.schemas import Event
from ogd.core.generators.extractors.PerLevelFeature import PerLevelFeature
from ogd.core.generators.Generator import ExtractorParameters
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData


"""class StoryAlignmentSequence(PerLevelFeature):
    def __init__(self, params: ExtractorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._story_alignment_sequence = []

    @classmethod
    def _getEventDependencies(cls, mode: ExtractionMode) -> List[str]:
        return ["story_updated"]

    @classmethod    
    def _getFeatureDependencies(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event: Event) -> None:
        self._story_alignment_sequence.append(event.EventData["story_alignment"])

    def _extractFromFeatureData(self, feature: FeatureData):
        return []

    def _getFeatureValues(self) -> List[Any]:
        return [self._story_alignment_sequence]

    def Subfeatures(self) -> List[str]:
        return []

    @classmethod
    def AvailableModes(cls) -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER, ExtractionMode.SESSION]"""


class StoryScoreSequence(PerLevelFeature):
    def __init__(self, params: ExtractorParameters):
        super().__init__(params=params)
        self._story_score_sequence = []

    @classmethod
    def _getEventDependencies(cls, mode: ExtractionMode) -> List[str]:
        return ["story_updated"]

    @classmethod
    def _getFeatureDependencies(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event: Event) -> None:
        self._story_score_sequence.append(event.event_data["story_score"])

    def _extractFromFeatureData(self, feature: FeatureData) -> None:
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._story_score_sequence]

    def Subfeatures(self) -> List[str]:
        return []

    @classmethod
    def AvailableModes(cls) -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER, ExtractionMode.SESSION]

