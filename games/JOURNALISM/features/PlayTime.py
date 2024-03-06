# import libraries
import json
from typing import Any, List, Optional
import json
from time import time
from datetime  import timedelta, datetime
# import local files
from extractors.features.Feature import Feature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
from extractors.Extractor import ExtractorParameters
from extractors.features.SessionFeature import SessionFeature





class PlayTime(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """

    IDLE_TIME_THRESHOLD = timedelta(seconds=60)


    def __init__(self, params:ExtractorParameters, threshold: int):
        super().__init__(params=params)
        self._last_event_timestamp : Optional[datetime] = None
        self._first_event_timestamp : Optional[datetime] = None
        
        
        self._idle_time : timedelta = timedelta(0)
        self._count : int = 0
        self._last_timestamp : Optional[datetime] = None
        self._threshold : timedelta = timedelta(seconds=threshold)
        self._total_time : Optional[timedelta] = None

        ##bugfixing
        self._user_log = None

    @staticmethod
    def defaultThreshold():
        return PlayTime.IDLE_TIME_THRESHOLD

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["all_events"] # >>> fill in names of events this Feature should use for extraction. <<<

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return [] # >>> fill in names of first-order features this Feature should use for extraction. <<<

    def _extractFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        

        if(not self._first_event_timestamp):
            self._first_event_timestamp = event.Timestamp

        
        if not self._last_event_timestamp:
            self._last_event_timestamp = event.Timestamp
            return
        if self._last_event_timestamp is not None:
            time_since_last = event.Timestamp - self._last_event_timestamp
            if time_since_last > PlayTime.IDLE_TIME_THRESHOLD:
                self._idle_time += time_since_last
                self._count += 1
        else:
            raise ValueError("In IdleState, last timestamp is None!")
        self._last_event_timestamp = event.Timestamp

        if(not event.UserID is None):
            self._user_log = event.UserID

        return

    def _extractFromFeatureData(self, feature: FeatureData):
        """_summary_

        :param feature: _description_
        :type feature: FeatureData
        """
        return

    def _getFeatureValues(self) -> List[Any]:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """

        #exception handling for empty sessions

        try:
            total_time : timedelta = self._last_event_timestamp - self._first_event_timestamp
            play_time : timedelta = total_time - self._idle_time

        except:
            total_time = 0
            play_time = 0


        return [total_time, play_time, self._idle_time]


    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["Active", "Idle"] # >>> fill in names of Subfeatures for which this Feature should extract values. <<<
    
    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.SESSION] # >>> delete any modes you don't want run for your Feature. <<<
    
    # @staticmethod
    # def MinVersion() -> Optional[str]:
    #     # >>> replace return statement below with a string defining the minimum logging version for events to be processed by this Feature. <<<
    #     return super().MinVersion()

    # @staticmethod
    # def MaxVersion() -> Optional[str]:
    #     # >>> replace return statement below with a string defining the maximum logging version for events to be processed by this Feature. <<<
    #     return super().MaxVersion()
