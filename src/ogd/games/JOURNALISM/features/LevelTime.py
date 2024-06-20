import logging
from datetime import datetime, timedelta
from ogd.games.JOURNALISM.features import PlayTime
from ogd.core.models import Event
from typing import Any, Final, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.extractors.PerLevelFeature import PerLevelFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class LevelTime(PerLevelFeature):
    def __init__(self, params:GeneratorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._begin_times    : List[datetime] = []
        self._complete_times : List[datetime] = []
        self._idle_time  : Optional[timedelta] = None
        self._total_time : Optional[timedelta] = None


    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["start_level", "complete_level"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["PlayTime"]

    def _validateEventCountIndex(self, event: Event):
        return self.CountIndex == 1
        


    def _updateFromEvent(self, event:Event) -> None:
        if event.EventName == "start_level":
            self._begin_times.append(event.Timestamp)
        elif event.EventName == "complete_level":
            self._complete_times.append(event.Timestamp)
        else:
            Logger.Log(f"LevelTime received an event which was not a BEGIN or a COMPLETE!", logging.WARN)

    def _updateFromFeatureData(self, feature:FeatureData):
        IDLE_TIME_INDEX : Final[int] = 2 # Idle time should be at index 2 for the PlayTime feature
        if feature.FeatureType == "PlayTime":
            self._idle_time = feature.FeatureValues[IDLE_TIME_INDEX]

    def _getFeatureValues(self) -> List[Any]:
        if len(self._begin_times) < len(self._complete_times):
            Logger.Log(f"Player began level {self.CountIndex} {len(self._begin_times)} times but completed it {len(self._complete_times)}.", logging.DEBUG)
        _num_plays = min(len(self._begin_times), len(self._complete_times))
        _diffs = [(self._complete_times[i] - self._begin_times[i]).total_seconds() for i in range(_num_plays)]
        self._total_time = sum(_diffs)
        total_time = self._total_time
        play_time = total_time - self._idle_time.total_seconds()
        return [play_time, total_time, self._idle_time]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["Total Time", "Idle Time"]
    
    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.SESSION]


