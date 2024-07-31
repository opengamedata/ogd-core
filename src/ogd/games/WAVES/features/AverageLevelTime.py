# import libraries
import logging
from datetime import datetime
from ogd.core.models import Event
from typing import Any, Dict, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class AverageLevelTime(SessionFeature):
    def __init__(self, params:GeneratorParameters):
        SessionFeature.__init__(self, params=params)
        self._levels_encountered : set                      = set()
        self._begin_times        : Dict[int,List[datetime]] = {}
        self._complete_times     : Dict[int,List[datetime]] = {}

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["BEGIN.0", "COMPLETE.0"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        _level = event.GameState['level']
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

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if len(self._begin_times) < len(self._complete_times):
            self.WarningMessage(f"Player began level {self.CountIndex} {len(self._begin_times)} times but completed it {len(self._complete_times)}.")
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
