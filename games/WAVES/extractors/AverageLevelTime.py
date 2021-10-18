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
                if level not in self._begin_times.keys() and level in self._complete_times.keys():
                    utils.Logger.Log(f"Player completed level {level}, but did not begin it!", logging.WARN)
                elif level in self._begin_times.keys() and level not in self._complete_times.keys():
                    utils.Logger.Log(f"Player began level {level}, but did not complete it.", logging.DEBUG)
                elif level not in self._begin_times.keys() and level not in self._complete_times.keys():
                    utils.Logger.Log(f"Player had level {level} listed as encountered, but did not begin *or* complete it.", logging.WARN)
        _total_time = sum(_diffs)
        if len(self._levels_encountered) > 0:
            return _total_time / len(self._levels_encountered)
        else:
            return None

    def _extractFromEvent(self, event:Event) -> None:
        _level = event.event_data['level']
        self._levels_encountered.add(_level) # set-add level to list, at end we will have set of all levels seen.
        if event.event_name == "BEGIN.0":
            self._begin_times[_level].append(event.timestamp)
        elif event.event_name == "COMPLETE.0":
            self._complete_times[_level].append(event.timestamp)
        else:
            utils.Logger.Log(f"AverageLevelTime received an event which was not a BEGIN or a COMPLETE!", logging.WARN)

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None


