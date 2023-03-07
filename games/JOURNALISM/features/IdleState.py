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





class IdleState(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    IDLE_TIME_THRESHOLD = timedelta(seconds=15)

    def __init__(self, params:ExtractorParameters, threshold: int):
        super().__init__(params=params)
        self._text_click_count : int = 0;
        self._time : timedelta = timedelta(0)
        self._count : int = 0
        self._last_timestamp : Optional[datetime] = None
        self._threshold : timedelta = timedelta(seconds=threshold)


        # >>> create/initialize any variables to track feature extractor state <<<
        #
        # e.g. To track whether extractor found a click event yet:
        # self._found_click : bool = False
    
    @staticmethod
    def defaultThreshold():
        return IdleState.IDLE_TIME_THRESHOLD

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
        # >>> use the data in the Event object to update state variables as needed. <<<
        # Note that this function runs once on each Event whose name matches one of the strings returned by _getEventDependencies()
        #
        # e.g. check if the event name contains the substring "Click," and if so set self._found_click to True
        if not self._last_timestamp:
            self._last_timestamp = event.Timestamp
            return
        if self._last_timestamp is not None:
            time_since_last = event.Timestamp - self._last_timestamp
            if time_since_last > IdleState.IDLE_TIME_THRESHOLD:
                self._time += time_since_last
                self._count += 1
        else:
            raise ValueError("In IdleState, last timestamp is None!")
        self._last_timestamp = event.Timestamp


        return

    def _extractFromFeatureData(self, feature: FeatureData):
        """_summary_

        :param feature: _description_
        :type feature: FeatureData
        """
        # >>> use data in the FeatureData object to update state variables as needed. <<<
        # Note: This function runs on data from each Feature whose name matches one of the strings returned by _getFeatureDependencies().
        #       The number of instances of each Feature may vary, depending on the configuration and the unit of analysis at which this CustomFeature is run.
        return

    def _getFeatureValues(self) -> List[Any]:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        
        return [self._time, self._count]


    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["Count"] # >>> fill in names of Subfeatures for which this Feature should extract values. <<<
    
    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.POPULATION, ExtractionMode.PLAYER, ExtractionMode.SESSION, ExtractionMode.DETECTOR] # >>> delete any modes you don't want run for your Feature. <<<
    
    # @staticmethod
    # def MinVersion() -> Optional[str]:
    #     # >>> replace return statement below with a string defining the minimum logging version for events to be processed by this Feature. <<<
    #     return super().MinVersion()

    # @staticmethod
    # def MaxVersion() -> Optional[str]:
    #     # >>> replace return statement below with a string defining the maximum logging version for events to be processed by this Feature. <<<
    #     return super().MaxVersion()
