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





class UserPlayTime(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._cumulative_play_time : Optional[timedelta] = None 
        self._cumulative_active_time : Optional[timedelta] = None
        


    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return [] # >>> fill in names of events this Feature should use for extraction. <<<

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["PlayTime"] # >>> fill in names of first-order features this Feature should use for extraction. <<<

    def _updateFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
    

        return

    def _updateFromFeatureData(self, feature: FeatureData):
        """_summary_

        :param feature: _description_
        :type feature: FeatureData
        """
        # >>> use data in the FeatureData object to update state variables as needed. <<<
        # Note: This function runs on data from each Feature whose name matches one of the strings returned by _featureFilter().
        #       The number of instances of each Feature may vary, depending on the configuration and the unit of analysis at which this CustomFeature is run.
    
        # Exception handling for empty sessions
        if(not self._cumulative_play_time):
            self._cumulative_play_time = feature._vals[0]
        if(not self._cumulative_active_time):
            self._cumulative_active_time = feature._vals[1]

        try:
            self._cumulative_play_time  += feature.FeatureValues[0]
            self._cumulative_active_time += feature.FeatureValues[1]
        except:
            self._cumulative_play_time += timedelta(0)
            self._cumulative_active_time += timedelta(0)

        
        
        return

    def _getFeatureValues(self) -> List[Any]:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """

        return [self._cumulative_play_time, self._cumulative_active_time]


    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["Active"] # >>> fill in names of Subfeatures for which this Feature should extract values. <<<
    
    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER] # >>> delete any modes you don't want run for your Feature. <<<
    
    # @staticmethod
    # def MinVersion() -> Optional[str]:
    #     # >>> replace return statement below with a string defining the minimum logging version for events to be processed by this Feature. <<<
    #     return super().MinVersion()

    # @staticmethod
    # def MaxVersion() -> Optional[str]:
    #     # >>> replace return statement below with a string defining the maximum logging version for events to be processed by this Feature. <<<
    #     return super().MaxVersion()
