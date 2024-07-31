# import libraries
import json
from typing import Any, Dict, List, Optional
# import local files
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.generators.extractors.PerLevelFeature import PerLevelFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature




class FailureAttributes(PerLevelFeature):
    """Per-level feature to generate a list of failures, where each failure in the list is the set of player attributes

    :param PerLevelFeature: Base class for a Custom Feature class.
    :type PerLevelFeature: _type_
    """
    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        PerLevelFeature.__init__(self, params=params)

        self._fails : List[Dict[str, int]] = []

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["level_fail"] # >>> fill in names of events this Feature should use for extraction. <<<

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
        attribs = ["endurance", "resourceful", "tech", "social", "trust", "research"]
        stats = json.loads(event.GameState.get("current_stats", str([None]*len(attribs))))
        self._fails.append(dict(zip(attribs, stats)))
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        """_summary_

        :param feature: _description_
        :type feature: FeatureData
        """
        # >>> use data in the FeatureData object to update state variables as needed. <<<
        # Note: This function runs on data from each Feature whose name matches one of the strings returned by _getFeatureDependencies().
        #       The number of instances of each Feature may vary, depending on the configuration and the unit of analysis at which this CustomFeature is run.
        return []

    def _getFeatureValues(self) -> List[Any]:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        return [self._fails]
    
    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.POPULATION, ExtractionMode.PLAYER, ExtractionMode.SESSION] # >>> delete any modes you don't want run for your Feature. <<<
