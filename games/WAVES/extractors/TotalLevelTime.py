from schemas import Event
import logging
from typing import Any, List, Union
# local imports
import utils
from extractors.Feature import Feature
from schemas.Event import Event

class TotalLevelTime(Feature):
    def __init__(self, name:str, description:str, count_index:int):
        Feature.__init__(self, name=name, description=description, count_index=count_index)
        self._begin_times = []
        self._complete_times = []

    def GetEventTypes(self) -> List[str]:
        return ["BEGIN", "COMPLETE"]

    def CalculateFinalValues(self) -> Any:
        if len(self._begin_times) != len(self._complete_times):
            utils.Logger.Log(f"Player began level {self._count_index} {len(self._begin_times)} times but only completed it {len(self._complete_times)}.", logging.WARN)
        _num_plays = min(len(self._begin_times), len(self._complete_times))
        _diffs = [(self._begin_times[i] - self._complete_times[i]).total_seconds() for i in range(_num_plays)]
        return sum(_diffs)

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_data["level"] == self._count_index:
            if event.event_name == "BEGIN":
                self._begin_times.append(event.timestamp)
            if event.event_name == "COMPLETE":
                self._complete_times.append(event.timestamp)

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None
