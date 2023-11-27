# import libraries
import logging
from datetime import datetime
from schemas import Event
from typing import Any, List, Optional
# import locals
from utils.Logger import Logger
from extractors.features.PerLevelFeature import PerLevelFeature
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData

class TotalLevelTime(PerLevelFeature):
    def __init__(self, params:ExtractorParameters):
        PerLevelFeature.__init__(self, params=params)
        self._begin_times    : List[datetime] = []
        self._complete_times : List[datetime] = []

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["BEGIN.0", "COMPLETE.0"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventName == "BEGIN.0":
            self._begin_times.append(event.Timestamp)
        elif event.EventName == "COMPLETE.0":
            self._complete_times.append(event.Timestamp)
        else:
            Logger.Log(f"AverageLevelTime received an event which was not a BEGIN or a COMPLETE!", logging.WARN)

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        if len(self._begin_times) < len(self._complete_times):
            Logger.Log(f"Player began level {self.CountIndex} {len(self._begin_times)} times but completed it {len(self._complete_times)}.", logging.DEBUG)
        _num_plays = min(len(self._begin_times), len(self._complete_times))
        _diffs = [(self._complete_times[i] - self._begin_times[i]).total_seconds() for i in range(_num_plays)]
        return [sum(_diffs)]

    # *** Optionally override public functions. ***
