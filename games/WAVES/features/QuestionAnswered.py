from schemas import Event
from typing import Any, List, Union
# local imports
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class QuestionAnswered(Feature):
    def __init__(self, name:str, description:str, count_index:int):
        Feature.__init__(self, name=name, description=description, count_index=count_index)
        self._answer = None

    def GetEventDependencies(self) -> List[str]:
        return ["CUSTOM.3"]
        # return ["QUESTION_ANSWER"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        return [self._answer]

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_data['question'] == self._count_index:
            self._answer = event.event_data['answered']

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None
