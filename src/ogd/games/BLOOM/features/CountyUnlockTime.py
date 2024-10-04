import logging
from datetime import datetime, timedelta
from typing import Any, List, Optional

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.games.BLOOM.features.PerCountyFeature import PerCountyFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from ogd.common.utils.Logger import Logger

class CountyUnlockTime(PerCountFeature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.time_started  : Optional[datetime]  = None
        self.last_time     : Optional[datetime]  = None
        self.total_time    : Optional[timedelta] = None
        self._unlock_count : int                 = 0
        self._skip_time    : timedelta           = timedelta(0)

    # Implement abstract functions
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["all_events", "game_start", "county_unlocked"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        event_type = event.EventName

        match (event_type):
            case "game_start":
                if self.time_started is None:
                    self.time_started = event.Timestamp
                elif self.last_time:
                    Logger.Log(f"Player {event.UserID} had more than one game_start event", logging.DEBUG)
                    self._skip_time += event.Timestamp - self.last_time
                else:
                    Logger.Log(f"Player {event.UserID} had more than one game_start event, with no previous events, somehow.", logging.WARNING)
            case "county_unlocked":
                self._unlock_count += 1
                county_name = event.EventData.get('county_name', "COUNTY NAME NOT FOUND")
                if self.time_started is not None and self.total_time is None:
                    self.total_time = (event.Timestamp - self.time_started) - self._skip_time
                elif self.time_started is None:
                    self.WarningMessage(f"Player {event.UserID} got a county_unlocked event for county {county_name} without a game_start event!")
                elif self.total_time is not None:
                    Logger.Log(f"Player {event.UserID} unlocked {county_name} more than once!", logging.DEBUG)
            case _:
                pass
        # No matter what, update last timestamp
        self.last_time = event.Timestamp

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self.total_time.total_seconds() if self.total_time is not None else None]

    def _validateEventCountIndex(self, event: Event):
        ret_val: bool = False

        match event.EventName:
            case "game_start":
                ret_val = True
            case "county_unlocked":
                county_name = event.EventData.get('county_name')
                if county_name is not None:
                    if self._getCountyIndex(county_name) == self.CountIndex:
                        ret_val = True
                else:
                    self.WarningMessage(f"In {type(self).__name__}, for event {event.EventName} with game state {event.EventData}, no county_name found.")
            case _:
                pass

        return ret_val

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"

    def _getCountyIndex(self, county_name: str) -> int:
        try:
            return PerCountyFeature.COUNTY_LIST.index(county_name)
        except ValueError:
            return -1
