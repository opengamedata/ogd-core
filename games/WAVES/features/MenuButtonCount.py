from schemas import Event
from typing import Any, List, Union
# local imports
from features.PerLevelFeature import PerLevelFeature
from schemas.Event import Event

class MenuButtonCount(PerLevelFeature):
    def __init__(self, name:str, description:str, count_index:int):
        PerLevelFeature.__init__(self, name=name, description=description, count_index=count_index)
        self._menu_btn_count = 0

    def GetEventDependencies(self) -> List[str]:
        return ["CUSTOM.5"]
        # "events": ["MENU_BUTTON"],

    def GetFeatureValues(self) -> List[Any]:
        return [self._menu_btn_count]

    def _extractFromEvent(self, event:Event) -> None:
        self._menu_btn_count += 1

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None
