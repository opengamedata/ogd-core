from schemas import Event
import typing
from typing import Any, List, Union
# local imports
from extractors.Feature import Feature
from schemas.Event import Event

class QuestionCorrect(Feature):
    def __init__(self, name:str, description:str, count_index:int):
        Feature.__init__(self, name=name, description=description, count_index=count_index)
        self._correct = None

    def GetEventTypes(self) -> List[str]:
        return ["CUSTOM.3"]
        # return ["QUESTION_ANSWER"]

    def CalculateFinalValues(self) -> Any:
        return self._correct

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_data['question'] == self._count_index:
            self._correct = (event.event_data['answered'] == event.event_data['answer'])

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None
