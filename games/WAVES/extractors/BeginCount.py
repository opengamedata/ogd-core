from schemas import Event
import typing
from typing import Any, List, Union
# local imports
from extractors.PerLevelFeature import PerLevelFeature
from schemas.Event import Event

class BeginCount(PerLevelFeature):
    def __init__(self, name:str, description:str, count_index:int):
        PerLevelFeature.__init__(self, name=name, description=description, count_index=count_index)
        self._num_begins = 0

    def GetEventTypes(self) -> List[str]:
        return ["BEGIN.0"]
        # return ["BEGIN"]

    def GetFeatureValues(self) -> Any:
        return self._num_begins

    def _extractFromEvent(self, event:Event) -> None:
        self._num_begins += 1

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None
