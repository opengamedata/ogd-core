# import libraries
from typing import Any, Final, List
# import local files
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
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
        return ["stat_update"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return []

    def _updateFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """

        self._top_names = []
        
        skill_vals = event.GameState.get("current_stats")
        if skill_vals:
            self._top_value = max(skill_vals.values())
            #get lowest val in list 
            self._top_names = [skill for skill,val in skill_vals if val == self._top_value]
        return

    def _updateFromFeatureData(self, feature: FeatureData):
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
