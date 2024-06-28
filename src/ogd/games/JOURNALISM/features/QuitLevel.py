# import libraries
import json
from typing import Any, List, Optional
import json
from time import time
from datetime  import timedelta, datetime
# import local files
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature





class QuitLevel(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._first_timestamp : Optional[datetime] = None
        self._current_timestamp : Optional[datetime]
        self._delta_time : Optional[timedelta] = None
        self._level_quit : int = 0
        self._last_event : Optional[str] = None
        self._node_id : Optional[str] = None

    

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
        
        if not self._first_timestamp:
            self._first_timestamp = event.Timestamp
            self._delta_time = timedelta(0)
        else:
            self._delta_time = event.Timestamp - self._first_timestamp
        
        self._last_event = event.event_name

        # Exception handling for events who don't have level or node_id attached to gamestate
        self._level_quit = event.GameState.get("level", None)
        self._node_id = event.EventData.get("node_id", "None")

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
        
        return [self._level_quit, self._last_event, self._node_id]


    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["EventName", "NodeID"] # >>> fill in names of Subfeatures for which this Feature should extract values. <<<
    
    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        ##don't make available for grouping by playerID
        return [ExtractionMode.PLAYER, ExtractionMode.SESSION] # >>> delete any modes you don't want run for your Feature. <<<
    
    # @staticmethod
    # def MinVersion() -> Optional[str]:
    #     # >>> replace return statement below with a string defining the minimum logging version for events to be processed by this Feature. <<<
    #     return super().MinVersion()

    # @staticmethod
    # def MaxVersion() -> Optional[str]:
    #     # >>> replace return statement below with a string defining the maximum logging version for events to be processed by this Feature. <<<
    #     return super().MaxVersion()
