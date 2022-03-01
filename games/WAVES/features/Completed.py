from os import truncate
from schemas import Event
from typing import Any, List, Union
# local imports
from features.PerLevelFeature import PerLevelFeature
from schemas.Event import Event

class Completed(PerLevelFeature):
    def __init__(self, name:str, description:str, count_index:int):
        PerLevelFeature.__init__(self, name=name, description=description, count_index=count_index)
        self._num_completes = 0

    def GetEventDependencies(self) -> List[str]:
        return ["COMPLETE.0"]

    def Subfeatures(self) -> List[str]:
        return ["Count"]

    def GetFeatureValues(self) -> List[Any]:
        return [self._num_completes > 0, self._num_completes]

    def _extractFromEvent(self, event:Event) -> None:
        self._num_completes += 1

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None
