from schemas import Event
import typing
from typing import Any, List, Union
# local imports
from extractors.PerLevelFeature import PerLevelFeature
from schemas.Event import Event

class TotalFails(PerLevelFeature):
    def __init__(self, name:str, description:str, count_index:int):
        PerLevelFeature.__init__(self, name=name, description=description, count_index=count_index)
        self._fail_count = 0

    def GetEventTypes(self) -> List[str]:
        return ["FAIL.0"]

    def GetFeatureValues(self) -> List[Any]:
        return self._fail_count

    def _extractFromEvent(self, event:Event) -> None:
        self._fail_count += 1

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None
