# import libraries
from typing import Any, List, Optional
from extractors.Extractor import ExtractorParameters
from datetime import date, datetime, time
# import local files
from extractors.features.SessionFeature import SessionFeature
from schemas.FeatureData import FeatureData
from schemas.Event import Event

class SessionStart(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._date : Optional[date] = None
        self._time : Optional[time] = None
        self._year : Optional[int] = None
        self._month : Optional[int] = None
        self._hour : Optional[int] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _getEventDependencies(self) -> List[str]:
        return ["CUSTOM.1"]

    def _getFeatureDependencies(self) -> List[str]:
        return [] 

    def _extractFromEvent(self, event:Event) -> None:
        event_time = event.Timestamp
        if not self._date:
            self._date = event_time.date()
            self._time = event_time.time()
            self._hour = event_time.hour
            self._year = event_time.year
            self._month = event_time.month


        return

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._date, self._time, self._year, self._month, self._hour]

    def Subfeatures(self) -> List[str]:
        return ["Time", "Year", "Month", "Hour"]

    def BaseFeatureSuffix(self) -> str:
        return "Date"

