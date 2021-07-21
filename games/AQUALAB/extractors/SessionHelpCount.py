from typing import Any, List

from extractors.Feature import Feature
from schemas.Event import Event

class SessionHelpCount(Feature):

    def __init__(self, name:str, description:str):
        min_data_version = None
        max_data_version = None
        super().__init__(name=name, description=description, count_index=0, min_version=min_data_version, max_version=max_data_version)
        self._count = 0

    def GetEventTypes(self) -> List[str]:
        return []

    def CalculateFinalValues(self) -> Any:
        return self._count

    def _extractFromEvent(self, event:Event) -> None:
        self._count += 1
