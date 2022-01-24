from schemas import Event
from typing import Any, List, Union
# local imports
from extractors.SessionFeature import SessionFeature
from schemas.Event import Event

class OverallSliderAverageStandardDeviations(SessionFeature):
    def __init__(self, name:str, description:str):
        SessionFeature.__init__(self, name=name, description=description)
        self._std_devs = []

    def GetEventTypes(self) -> List[str]:
        return ["CUSTOM.1"]
        # return ["SLIDER_MOVE_RELEASE"]

    def GetFeatureValues(self) -> List[Any]:
        if len(self._std_devs) > 0:
            return [sum(self._std_devs) / len(self._std_devs)]
        else:
            return [None]

    def _extractFromEvent(self, event:Event) -> None:
        self._std_devs.append(event.event_data["stdev_val"])

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None


