# import libraries
from typing import Any, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
# import local files
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.models.Event import Event

class UserEnabled(SessionFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._full_screen : Optional[int] = None
        self._music : Optional[int] = None
        self._hq : Optional[int] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.1"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return [] 

    def _updateFromEvent(self, event:Event) -> None:
        _data = event.EventData
        true_values = ["1", "true"]
        for item in ["fullscreen", "music", "hq"]:
            if _data.get(item) is None:
                raise(ValueError(f"Can't find {item} item in the event data!"))
        if str(_data.get("fullscreen")).lower() in true_values:
            self._full_screen = 1
        else:
            self._full_screen = 0

        if str(_data.get("music")).lower() in true_values:
            self._music = 1
        else:
            self._music = 0

        if str(_data.get("hq")).lower() in true_values:
            self._hq = 1
        else:
            self._hq = 0

        return

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._full_screen, self._music, self._hq]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["Music", "HQGraphics"] 

    def BaseFeatureSuffix(self) -> str:
        return "FullScreen"