# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from utils.Logger import Logger
from extractors.Extractor import ExtractorParameters
from extractors.features.Feature import Feature
from extractors.features.SessionFeature import SessionFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
scenes_map = {"ICE":0, "VOYAGER":0, "NOTHING":0, "EXTREME":0, "EARTH":0, "CREDITS":0}

class ViewportCountPerScene(SessionFeature):

    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._failure_count : int = 0
        self._scene_started = False
        self._cnt_dict = scenes_map.copy()
        self._curr_scene = None
        self._scene_list = list()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["scene_change", "viewport_data"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.EventName == "scene_change":
            self._scene_list.append(event.event_data.get("scene_name"))
        elif event.EventName == "viewport_data":
            self._curr_scene = self._scene_list[-1]
            self._cnt_dict[self._curr_scene] += 1
        return
    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._cnt_dict]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "2"