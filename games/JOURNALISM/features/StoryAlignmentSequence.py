# import libraries
from typing import Any, List
from schemas import Event
from extractors.features.PerLevelFeature import PerLevelFeature
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData

"""
class StoryAlignmentSequence(PerLevelFeature):
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
        self._story_alignment_sequence.append(event.event_data["story_alignment"])

    def _extractFromFeatureData(self, feature: FeatureData):
        return []

    def _getFeatureValues(self) -> List[Any]:
        return [self._story_alignment_sequence]

    def Subfeatures(self) -> List[str]:
        return []

    @classmethod
    def AvailableModes(cls) -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER, ExtractionMode.SESSION]
"""



class StoryAlignmentSequence(PerLevelFeature):
    def __init__(self, params: ExtractorParameters):
        super().__init__(params=params)
        self._story_alignment_sequence = []

    @classmethod
    def _getEventDependencies(cls, mode: ExtractionMode) -> List[str]:
        return ["story_updated"]

    @classmethod
    def _getFeatureDependencies(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event: Event) -> None:
        self._story_alignment_sequence.append(event.event_data["story_alignment"])

    def _extractFromFeatureData(self, feature: FeatureData) -> None:
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._story_alignment_sequence]

    def Subfeatures(self) -> List[str]:
        return []

    @classmethod
    def AvailableModes(cls) -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER, ExtractionMode.SESSION]

