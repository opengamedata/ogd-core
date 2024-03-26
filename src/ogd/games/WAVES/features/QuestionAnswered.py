# import libraries
from ogd.core.schemas import Event
from typing import Any, List, Optional
# import locals
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData


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

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventData['question'] == self.CountIndex:
            self._answer = event.EventData['answered']

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._answer]

    # *** Optionally override public functions. ***
