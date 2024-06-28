# import libraries
from typing import Any, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
# import local files
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.models.Event import Event


# regexpr to test num: "fqid": ".{1,800}"(navigate|map)", "type": "click"

class MeaningfulActions(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._click_count : int = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.3", "CUSTOM.5"]
        # ["CUSTOM.3", "CUSTOM.5"] = ["Navigation_click", "map_click"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        # fqid != 0 means that the click event does make Jo move to some interactive items, such as an interaction, an item that Jo can look into, or a way to next room.
        if event.EventData.get("fqid") != 0:
            self._click_count += 1
        return

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:

        return [self._click_count]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return []
