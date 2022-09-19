# import libraries
from schemas import Event
from typing import Any, List, Optional
# import locals
from extractors.features.Feature import Feature
from schemas.FeatureData import FeatureData
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event

class QuestionCorrect(Feature):
    def __init__(self, params:ExtractorParameters):
        Feature.__init__(self, params=params)
        self._correct = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
def _getEventDependencies(cls, mode:ExportMode) -> List[str]:
        return ["CUSTOM.3"]
        # return ["QUESTION_ANSWER"]

    @classmethod
def _getEventDependencies(cls, mode:ExportMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventData['question'] == self.CountIndex:
            self._correct = (event.EventData['answered'] == event.EventData['answer'])

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._correct]

    # *** Optionally override public functions. ***
