import typing
from typing import Any, List, Union
# local imports
from extractors.PerLevelFeature import PerLevelFeature
from schemas.Event import Event

class SliderAverageStandardDeviations(PerLevelFeature):
    def __init__(self, name:str, description:str, count_index:int):
        PerLevelFeature.__init__(self, name=name, description=description, count_index=count_index)
        self._std_devs = []

    def GetEventTypes(self) -> List[str]:
        return ["CUSTOM.1"]
        # return ["SLIDER_MOVE_RELEASE"]

    def GetFeatureValues(self) -> Any:
        if len(self._std_devs) > 0:
            return sum(self._std_devs) / len(self._std_devs)
        else:
            return None

    def _extractFromEvent(self, event:Event) -> None:
        self._std_devs.append(event.event_data["stdev_val"])

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None
