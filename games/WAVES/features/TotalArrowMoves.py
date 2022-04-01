# import libraries
from schemas import Event
from typing import Any, List, Union
# import locals
from features.FeatureData import FeatureData
from features.PerLevelFeature import PerLevelFeature
from schemas.Event import Event

class TotalArrowMoves(PerLevelFeature):
    def __init__(self, name:str, description:str, count_index:int):
        PerLevelFeature.__init__(self, name=name, description=description, count_index=count_index)
        self._arrow_move_count : int = 0

    # *** Implement abstract functions ***
    def _getEventDependencies(self) -> List[str]:
        return ["CUSTOM.2"]
        # return ["ARROW_MOVE_RELEASE"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._arrow_move_count += 1

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._arrow_move_count]

    # *** Optionally override public functions. ***
