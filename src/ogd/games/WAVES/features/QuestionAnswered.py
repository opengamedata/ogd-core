# import libraries
from ogd.common.models import Event
from typing import Any, List, Optional
# import locals
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData


class QuestionAnswered(Feature):
    def __init__(self, params:GeneratorParameters):
        Feature.__init__(self, params=params)
        self._answer = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.3"]
        # return ["QUESTION_ANSWER"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if event.EventData['question'] == self.CountIndex:
            self._answer = event.EventData['answered']

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._answer]

    # *** Optionally override public functions. ***
