# import libraries
from typing import Any, List
from ogd.core.models import Event
from ogd.core.generators.extractors.PerLevelFeature import PerLevelFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

"""
class StoryAlignmentSequence(PerLevelFeature):
    def __init__(self, params: GeneratorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._story_alignment_sequence = []
        
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["story_updated"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        self._story_alignment_sequence.append(event.event_data["story_alignment"])

    def _updateFromFeatureData(self, feature: FeatureData):
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
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self._story_alignment_sequence = []

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["story_updated"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        self._story_alignment_sequence.append(event.event_data["story_alignment"])

    def _updateFromFeatureData(self, feature: FeatureData) -> None:
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._story_alignment_sequence]

    def Subfeatures(self) -> List[str]:
        return []

    @classmethod
    def AvailableModes(cls) -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER, ExtractionMode.SESSION]

