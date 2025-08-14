# import libraries
from datetime import datetime, timedelta
import logging, warnings
from typing import Any, List, Optional
# import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.extractors.Extractor import GeneratorParameters
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature

class TotalPlayTime(Extractor):
    def __init__(self, params:GeneratorParameters, ):
        super().__init__(params=params)
        self._play_time: timedelta = timedelta(0)
        self._play_time_seconds: timedelta = timedelta(0)
        self._idle_time: timedelta = timedelta(0)
        self._idle_time_seconds: timedelta = timedelta(0)
        self._active_time: timedelta = timedelta(0)
        self._active_time_seconds: timedelta = timedelta(0)
    def Subfeatures(self) -> List[str]:
        return ["Seconds", "Active", "Active - Seconds", "Idle", "Idle - Seconds"]
    
    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["SessionDuration"]

    def _updateFromEvent(self, event:Event) -> None:
        pass

    def _updateFromFeature(self, feature:Feature):
        if feature.ExportMode == ExtractionMode.SESSION:
            try:
                self._play_time += feature.Values[0]
                self._play_time_seconds += feature.Values[1]
                self._active_time += feature.Values[2]
                self._active_time_seconds += feature.Values[3]
                self._idle_time += feature.Values[4]
                self._idle_time += feature.Values[5]
            except TypeError as err:
                self.WarningMessage(f"TotalPlayTime for player {feature.PlayerID} got non-timedelta value of {feature.Values[0]}")
    
    def _getFeatureValues(self) -> List[Any]:
        return [self._play_time, self._play_time_seconds, self._active_time, self._active_time_seconds, self._idle_time, self._idle_time_seconds]

    # *** Optionally override public functions. ***

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER]
