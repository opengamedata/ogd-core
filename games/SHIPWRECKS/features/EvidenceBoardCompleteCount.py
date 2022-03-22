from typing import Any, List, Union

from features.FeatureData import FeatureData
from features.Feature import Feature
from schemas.Event import Event

class EvidenceBoardCompleteCount(Feature):

    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description)
        self._count = 0

    def GetEventDependencies(self) -> List[str]:
        return ["evidence_board_complete"]

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        return [self._count]

    def MinVersion(self) -> Union[str,None]:
        return "1"

    def _extractFromEvent(self, event:Event) -> None:
        self._count += 1

    def _extractFromFeatureData(self, feature: FeatureData):
        return
