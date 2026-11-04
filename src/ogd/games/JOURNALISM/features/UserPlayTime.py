# import libraries
import json
from typing import Any, List, Optional
import json
from time import time
from datetime  import timedelta, datetime
# import local files
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
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
    
        # Exception handling for empty sessions: a PlayTime instance that saw no
        # events can report None, so neither the seed nor the accumulation may
        # assume a timedelta is present.
        if self._cumulative_play_time is None:
            self._cumulative_play_time = timedelta(0)
        if self._cumulative_active_time is None:
            self._cumulative_active_time = timedelta(0)

        _vals = feature.FeatureValues

        _play_time = _vals[0] if len(_vals) > 0 else None
        if isinstance(_play_time, timedelta):
            self._cumulative_play_time += _play_time

        _active_time = _vals[1] if len(_vals) > 1 else None
        if isinstance(_active_time, timedelta):
            self._cumulative_active_time += _active_time

        
        
        return

    def _getFeatureValues(self) -> List[Any]:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """

        # A player whose sessions all produced no PlayTime data never reaches
        # _updateFromFeatureData, leaving these as None; report zeroes rather
        # than crashing the whole export (see AttributeError on .total_seconds).
        _play_time   = self._cumulative_play_time   if self._cumulative_play_time   is not None else timedelta(0)
        _active_time = self._cumulative_active_time if self._cumulative_active_time is not None else timedelta(0)

        return [_play_time, _active_time, _active_time.total_seconds()]


    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["Active", "Active-Seconds"] # >>> fill in names of Subfeatures for which this Feature should extract values. <<<
    
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
