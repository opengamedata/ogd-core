import typing
from typing import Any, List, Union
# local imports
from features.PerLevelFeature import PerLevelFeature
from schemas.Event import Event

class SucceedCount(PerLevelFeature):
    def __init__(self, name:str, description:str, count_index:int):
        PerLevelFeature.__init__(self, name=name, description=description, count_index=count_index)
        self._succeed_count = 0

    def GetEventDependencies(self) -> List[str]:
        return ["SUCCEED.0"]

    def GetFeatureValues(self) -> List[Any]:
        return [self._succeed_count]

    def _extractFromEvent(self, event:Event) -> None:
        self._succeed_count += 1

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None
