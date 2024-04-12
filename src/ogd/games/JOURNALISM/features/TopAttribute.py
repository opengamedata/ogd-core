# import libraries
import json
from typing import Any, Final, List
# import local files
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.FeatureData import FeatureData
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature




class TopAttribute(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._top_value : int = 0
        self._top_names : List[str] = []
        self._ATTRIBUTE_ENUM : Final[List[str]] = ["endurance", "resourceful", "tech","social","trust","research"]
        #self._text_click_count : int = 0;
        # >>> create/initialize any variables to track feature extractor state <<<
        #
        # e.g. To track whether extractor found a click event yet:
        # self._found_click : bool = False

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["stat_update"] # >>> fill in names of events this Feature should use for extraction. <<<

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

        self._top_names = []
        
        skill_vals = eval(event.GameState["current_stats"])
        self._top_value = max(skill_vals)
        #get lowest val in list 
        res_list = [i for i in range(len(skill_vals)) if skill_vals[i] == self._top_value]

        for val in res_list:
            self._top_names.append(self._ATTRIBUTE_ENUM[val])



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
        
        # >>> use state variables to calculate the return value(s) of the base Feature and any Subfeatures. <<<
        # >>> put the calculated value(s) into a list as the function return value. <<<
        # >>> definitely don't return ["template"], unless you really find that useful... <<<
        #
        # e.g. use the self._found_click, which was created/initialized in __init__(...), and updated in _updateFromEvent(...):
        # if self._found_click:
        #     ret_val = [True]
        # else:
        #     ret_val = [False]
        # return ret_val
        #
        # note the code above is redundant, we could just return [self._found_click] to get the same result;
        # the more-verbose code is here for illustrative purposes.
        return [self._top_value,self._top_names]


    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["Names"] # >>> fill in names of Subfeatures for which this Feature should extract values. <<<
    
    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER, ExtractionMode.SESSION] # >>> delete any modes you don't want run for your Feature. <<<
    
    # @staticmethod
    # def MinVersion() -> Optional[str]:
    #     # >>> replace return statement below with a string defining the minimum logging version for events to be processed by this Feature. <<<
    #     return super().MinVersion()

    # @staticmethod
    # def MaxVersion() -> Optional[str]:
    #     # >>> replace return statement below with a string defining the maximum logging version for events to be processed by this Feature. <<<
    #     return super().MaxVersion()
