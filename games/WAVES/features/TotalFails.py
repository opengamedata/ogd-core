from schemas import Event
import typing
from typing import Any, List, Optional
# import locals
from schemas.FeatureData import FeatureData
from features.PerLevelFeature import PerLevelFeature
from schemas.Event import Event

class TotalFails(PerLevelFeature):
    def __init__(self, name:str, description:str, count_index:int):
        PerLevelFeature.__init__(self, name=name, description=description, count_index=count_index)
        self._fail_count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["FAIL.0"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._fail_count += 1

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._fail_count]

    # *** Optionally override public functions. ***
