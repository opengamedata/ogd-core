# import libraries
from schemas import Event
from typing import Any, List, Union
# import locals
from schemas.FeatureData import FeatureData
from features.PerLevelFeature import PerLevelFeature
from schemas.Event import Event

class MenuButtonCount(PerLevelFeature):
    def __init__(self, name:str, description:str, count_index:int):
        PerLevelFeature.__init__(self, name=name, description=description, count_index=count_index)
        self._menu_btn_count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["CUSTOM.5"]
        # "events": ["MENU_BUTTON"],

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._menu_btn_count += 1

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._menu_btn_count]

    # *** Optionally override public functions. ***
