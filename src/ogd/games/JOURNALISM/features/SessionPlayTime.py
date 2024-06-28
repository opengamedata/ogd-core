# import libraries
import json
from typing import Any, Final, List, Optional
import json
from datetime  import timedelta, datetime
# import local files
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature





class SessionPlayTime(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    IDLE_TIME_THRESHOLD : Final[timedelta] = timedelta(seconds=60)

    def __init__(self, params:GeneratorParameters, threshold: int):
        super().__init__(params=params)
        self._first_event_timestamp : Optional[datetime] = None
        self._last_event_timestamp : Optional[datetime] = None

        self._idle_time : Optional[timedelta] = None
        self._time : timedelta = timedelta(0)
        self._count : int = 0
        self._last_timestamp : Optional[datetime] = None
        self._threshold : timedelta = timedelta(seconds=threshold)
        self._total_time : Optional[timedelta] = None

        # >>> create/initialize any variables to track feature extractor state <<<
        #
        # e.g. To track whether extractor found a click event yet:
        # self._found_click : bool = False
    
    @staticmethod
    def defaultThreshold():
        return SessionPlayTime.IDLE_TIME_THRESHOLD

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["all_events"] # >>> fill in names of events this Feature should use for extraction. <<<

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return [] # >>> fill in names of first-order features this Feature should use for extraction. <<<

    def _updateFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        # >>> use the data in the Event object to update state variables as needed. <<<
        # Note that this function runs once on each Event whose name matches one of the strings returned by _eventFilter()
        #
        # e.g. check if the event name contains the substring "Click," and if so set self._found_click to True
        if not self._first_event_timestamp:
            self._first_event_timestamp = event.Timestamp

        if not self._last_timestamp:
            self._last_timestamp = event.Timestamp
            print("set self._last!")
            return
        if self._last_timestamp is not None:
            time_since_last = event.Timestamp - self._last_timestamp
            if time_since_last > SessionPlayTime.IDLE_TIME_THRESHOLD:
                self._time += time_since_last
                self._count += 1
        else:
            raise ValueError("In IdleState, last timestamp is None!")
        self._last_timestamp = event.Timestamp

        if(not self._first_event_timestamp):
            self._first_event_timestamp = event.Timestamp
        
        self._last_event_timestamp = event.Timestamp


        return

    def _updateFromFeatureData(self, feature: FeatureData):
        """_summary_

        :param feature: _description_
        :type feature: FeatureData
        """
        # >>> use data in the FeatureData object to update state variables as needed. <<<
        # Note: This function runs on data from each Feature whose name matches one of the strings returned by _featureFilter().
        #       The number of instances of each Feature may vary, depending on the configuration and the unit of analysis at which this CustomFeature is run.
        return

    def _getFeatureValues(self) -> List[Any]:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        # print(f'_first_timestamp is:{self._first_event_timestamp}, _last_timestamp is: {self._last_timestamp}')
        
        # if(not self._first_event_timestamp):
        #     self._total_time = 0
        #     play_time : int = 0
        # else:
        #     self._total_time = self._last_timestamp-self._first_event_timestamp
        #     play_time : timedelta = self._total_time - self._time

        #total idle time, idle count, total session time, (total session time - idle time)
        # return [self._time, self._count, self._total_time, play_time]
        total_time : timedelta = self._last_event_timestamp - self._first_event_timestamp

        return [total_time, 0, 0, 0]


    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["Count", "Total Time", "Total Play Time"] # >>> fill in names of Subfeatures for which this Feature should extract values. <<<
    
    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.POPULATION, ExtractionMode.PLAYER, ExtractionMode.SESSION] # >>> delete any modes you don't want run for your Feature. <<<
    
    # @staticmethod
    # def MinVersion() -> Optional[str]:
    #     # >>> replace return statement below with a string defining the minimum logging version for events to be processed by this Feature. <<<
    #     return super().MinVersion()

    # @staticmethod
    # def MaxVersion() -> Optional[str]:
    #     # >>> replace return statement below with a string defining the maximum logging version for events to be processed by this Feature. <<<
    #     return super().MaxVersion()
