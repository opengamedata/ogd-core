# import libraries
from os import truncate
from schemas import Event
from typing import Any, List, Optional
# import locals
from extractors.features.PerLevelFeature import PerLevelFeature
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData

class LevelStoryAlignment(PerLevelFeature):
    def __init__(self, params:ExtractorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._story_alignment = 0
        ##print("working!")


    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["display_feedback_dialog"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._story_alignment = event.EventData["story_alignment"]

    def _extractFromFeatureData(self, feature:FeatureData):
        print("extracting!")
        return []

    def _getFeatureValues(self) -> List[Any]:
        return [self._story_alignment]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return []
