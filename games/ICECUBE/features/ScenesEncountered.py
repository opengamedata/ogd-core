# import libraries
import json
from typing import Any, List, Optional
# import local files
from extractors.Extractor import ExtractorParameters
from extractors.features.Feature import Feature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData


class ScenesEncountered(Feature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._scenes = set()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["scene_change", "scene_changed"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return []

    def _extractFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        self._scenes.add(event.EventData.get("scene_name", "NO_SCENE_CHANGE"))

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
        ret_val : List[Any] = [list(self._scenes)]
        return ret_val

    # *** Optionally override public functions. ***
    
    @staticmethod
    def MinVersion() -> Optional[str]:
        # >>> replace return statement below with a string defining the minimum logging version for events to be processed by this Feature. <<<
        return "2"

    @staticmethod
    def MaxVersion() -> Optional[str]:
        # >>> replace return statement below with a string defining the maximum logging version for events to be processed by this Feature. <<<
        return super().MaxVersion()
