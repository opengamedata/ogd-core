# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from utils import Logger
from extractors.Extractor import ExtractorParameters
from extractors.features.Feature import Feature
from extractors.features.SessionFeature import SessionFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData

class ScenesEncountered(SessionFeature):

    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._scene_name = None
        self._cnt_list = list()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["scene_change"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._scene_name = event.EventData.get("scene_name")
        self._cnt_list.append(self._scene_name)

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._cnt_list]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "2"