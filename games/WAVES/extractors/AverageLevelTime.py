# global imports
import logging
from datetime import datetime
from schemas import Event
from typing import Any, Dict, List, Union
# local imports
import utils
from extractors.SessionFeature import SessionFeature
from schemas.Event import Event

class AverageLevelTime(SessionFeature):
    def __init__(self, name:str, description:str):
        SessionFeature.__init__(self, name=name, description=description)
        self._levels_encountered : set                      = set()
        self._begin_times        : Dict[int,List[datetime]] = {}
        self._complete_times     : Dict[int,List[datetime]] = {}

    def GetEventTypes(self) -> List[str]:
        return ["BEGIN.0", "COMPLETE.0"]

    def CalculateFinalValues(self) -> Any:
        if len(self._begin_times) != len(self._complete_times):
            utils.Logger.Log(f"Player began level {self._count_index} {len(self._begin_times)} times but only completed it {len(self._complete_times)}.", logging.WARN)
        _num_plays  = min(len(self._begin_times), len(self._complete_times))
        _diffs      = []
        for level in self._levels_encountered:
            if level in self._begin_times.keys() and level in self._complete_times.keys():
                _diffs += [(self._begin_times[level][i] - self._complete_times[level][i]).total_seconds() for i in range(_num_plays)]
            else:
                utils.Logger.Log(f"Player began or completed level {level}, but did not begin *and* complete it.", logging.WARN)
        _total_time = sum(_diffs)
        return _total_time / len(self._levels_encountered)

    def _extractFromEvent(self, event:Event) -> None:
        _level = event.event_data['level']
        self._levels_encountered.add(_level) # set-add level to list, at end we will have set of all levels seen.
        if event.event_name == "BEGIN":
            self._begin_times[_level].append(event.timestamp)
        if event.event_name == "COMPLETE":
            self._complete_times[_level].append(event.timestamp)

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None


