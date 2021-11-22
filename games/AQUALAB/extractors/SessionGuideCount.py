from typing import Any, List

from extractors.Feature import Feature
from schemas.Event import Event

class SessionGuideCount(Feature):

    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0)
        self._count = 0

    def GetEventTypes(self) -> List[str]:
        return ["guide_triggered"]

    def GetFeatureValues(self) -> List[Any]:
        return self._count

    def _extractFromEvent(self, event:Event) -> None:
        self._count += 1
