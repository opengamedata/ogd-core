# import libraries
from typing import Any, List, Optional
from extractors.Extractor import ExtractorParameters
# import local files
from extractors.features.SessionFeature import SessionFeature
from schemas.FeatureData import FeatureData
from schemas.Event import Event


# regexpr to test num: "fqid": ".{1,800}"(navigate|map)", "type": "click"

class MeaningfulActions(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._click_count : int = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _getEventDependencies(self) -> List[str]:
        return ["CUSTOM.3", "CUSTOM.5"]
        # ["CUSTOM.3", "CUSTOM.5"] = ["Navigation_click", "map_click"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventData.get("fqid") != 0:
            self._click_count += 1
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:

        return [self._click_count]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return []
