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





class QuitType(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """

    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        
        ##event boolean watchers
        self._last_event: Optional[str] = None
        self._display_feedback: bool = False
        self._start_level: bool = False

        ##feature boolean watchers
        self._between_levels : bool = False
        self._on_fail : bool = False
        self._other : bool = False

    

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
        
        # if(self._display_feedback == True & self._start_level == True)
        
        # if(event.EventName == "start_level"):
        #     self._display_feedback = False
        #     self._start_level = True

        # if(event.EventName == "display_feedback_dialog"):
        #     self._display_feedback = True
        #     self._start_level = False
        #     self._between_levels = True
        #     self._other, self._on_fail = False

        ##During the window of events between display_feedback_dialog -> start_level, 
        ##_between_levels = True. Otherwise, _other= True
        if(event.EventName == "display_feedback_dialog"):
            self._start_level = False
            self._display_feedback = True
            self._between_levels, self._other = True, False

        if(event.EventName == "start_level"):
            self._start_level = True
            if(self._display_feedback == True):
                self._display_feedback = False
                self._between_levels, self._other = False, True
        
        if(event.EventName == "time_expired"):
            self._between_levels, self._other = False, False
            self._on_fail = True




        
        

        # if(event.EventName == "display_feedback_dialog"):
        #     self._display_feedback = True
        # elif(event.EventName == "start_level"):
        #     self._start_level = True
        #     if(self._display_feedback == True):
        #         self._between_levels 



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
        
        return [self._delta_time, self._level_quit, self._last_event]


    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["Level", "EventName"] # >>> fill in names of Subfeatures for which this Feature should extract values. <<<
    
    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        ##don't make available for grouping by playerID
        return [ExtractionMode.PLAYER, ExtractionMode.SESSION, ExtractionMode.DETECTOR] # >>> delete any modes you don't want run for your Feature. <<<
    
    # @staticmethod
    # def MinVersion() -> Optional[str]:
    #     # >>> replace return statement below with a string defining the minimum logging version for events to be processed by this Feature. <<<
    #     return super().MinVersion()

    # @staticmethod
    # def MaxVersion() -> Optional[str]:
    #     # >>> replace return statement below with a string defining the maximum logging version for events to be processed by this Feature. <<<
    #     return super().MaxVersion()
