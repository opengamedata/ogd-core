# import libraries
from os import truncate
from ogd.core.models import Event
from typing import Any, List, Optional
# import locals
from ogd.core.generators.extractors.PerLevelFeature import PerLevelFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class StoryAlignment(PerLevelFeature):
    def __init__(self, params:GeneratorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._story_alignment = 0
        ##print("working!")


    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["display_feedback_dialog"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        self._story_alignment = event.EventData["story_alignment"]

    def _updateFromFeatureData(self, feature:FeatureData):
        print("extracting!")
        return []

    def _getFeatureValues(self) -> List[Any]:
        return [self._story_alignment]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return []
