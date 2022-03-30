# global imports
from schemas import Event
import typing
from typing import Any, List, Union
# local imports
from features.FeatureData import FeatureData
from features.PerLevelFeature import PerLevelFeature
from schemas.Event import Event

class TotalResets(PerLevelFeature):
    def __init__(self, name:str, description:str, count_index:int):
        PerLevelFeature.__init__(self, name=name, description=description, count_index=count_index)
        self._reset_count = 0

    # *** Implement abstract functions ***
    def _getEventDependencies(self) -> List[str]:
        return ["CUSTOM.4"]
        # "events": ["RESET_BTN_PRESS"],

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._reset_count += 1

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._reset_count]

    # *** Optionally override public functions. ***
