# import libraries
import logging
from datetime import datetime
from schemas import Event
from typing import Any, Dict, List, Optional
# import locals
from utils import Logger
from schemas.FeatureData import FeatureData
from features.SessionFeature import SessionFeature
from schemas.Event import Event

class AverageLevelTime(SessionFeature):
    def __init__(self, name:str, description:str):
        SessionFeature.__init__(self, name=name, description=description)
        self._levels_encountered : set                      = set()
        self._begin_times        : Dict[int,List[datetime]] = {}
        self._complete_times     : Dict[int,List[datetime]] = {}

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["BEGIN.0", "COMPLETE.0"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        _level = event.EventData['level']
        self._levels_encountered.add(_level) # set-add level to list, at end we will have set of all levels seen.
        if event.EventName == "BEGIN.0":
            if not _level in self._begin_times.keys():
                self._begin_times[_level] = []
            self._begin_times[_level].append(event.Timestamp)
        elif event.EventName == "COMPLETE.0":
            if not _level in self._complete_times.keys():
                self._complete_times[_level] = []
            self._complete_times[_level].append(event.Timestamp)
        else:
            Logger.Log(f"AverageLevelTime received an event which was not a BEGIN or a COMPLETE!", logging.WARN)

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if len(self._begin_times) < len(self._complete_times):
            Logger.Log(f"Player began level {self.CountIndex} {len(self._begin_times)} times but completed it {len(self._complete_times)}.", logging.WARNING)
        _diffs      = []
        for level in self._levels_encountered:
            if level in self._begin_times.keys() and level in self._complete_times.keys():
                _num_plays  = min(len(self._begin_times[level]), len(self._complete_times[level]))
                _diffs += [(self._complete_times[level][i] - self._begin_times[level][i]).total_seconds() for i in range(_num_plays)]
            else:
                if level not in self._begin_times.keys() and level in self._complete_times.keys():
                    Logger.Log(f"Player completed level {level}, but did not begin it!", logging.WARN)
                elif level in self._begin_times.keys() and level not in self._complete_times.keys():
                    Logger.Log(f"Player began level {level}, but did not complete it.", logging.DEBUG)
                elif level not in self._begin_times.keys() and level not in self._complete_times.keys():
                    Logger.Log(f"Player had level {level} listed as encountered, but did not begin *or* complete it.", logging.WARN)
        _total_time = sum(_diffs)
        if len(self._levels_encountered) > 0:
            return [_total_time / len(self._levels_encountered)]
        else:
            return [None]

    # *** Optionally override public functions. ***
