# import libraries
from typing import Any, List
# import locals
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class MoveShapeCount(Feature):
    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0)
        self._count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["move_shape"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._count += 1

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***
