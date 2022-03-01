from typing import Any, List

from features.Feature import Feature
from schemas.Event import Event

class SwitchJobsCount(Feature):
    
    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0)
        self._count = 0

    def GetEventDependencies(self) -> List[str]:
        return ["switch_job"]

    def GetFeatureValues(self) -> List[Any]:
        return [self._count]

    def _extractFromEvent(self, event:Event) -> None:
        self._count += 1
