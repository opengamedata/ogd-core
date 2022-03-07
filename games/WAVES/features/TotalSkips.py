from schemas import Event
import typing
from typing import Any, List, Union
# local imports
from features.FeatureData import FeatureData
from features.PerLevelFeature import PerLevelFeature
from schemas.Event import Event

class TotalSkips(PerLevelFeature):
    def __init__(self, name:str, description:str, count_index:int):
        PerLevelFeature.__init__(self, name=name, description=description, count_index=count_index)
        self._skip_count = 0

    def GetEventDependencies(self) -> List[str]:
        return ["CUSTOM.6"]
        # "events": ["SKIP_BUTTON"],

    def GetFeatureDependencies(self) -> List[str]:
        return []

    def GetFeatureValues(self) -> List[Any]:
        return [self._skip_count]

    def _extractFromEvent(self, event:Event) -> None:
        self._skip_count += 1

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None
