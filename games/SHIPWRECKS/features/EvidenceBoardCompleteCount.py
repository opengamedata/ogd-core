# import libraries
from typing import Any, List, Union
# import locals
from schemas.FeatureData import FeatureData
from features.Feature import Feature
from schemas.Event import Event

class EvidenceBoardCompleteCount(Feature):

    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description)
        self._count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["evidence_board_complete"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._count += 1

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***