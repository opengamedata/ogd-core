# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
scenes_map = {"ICE":0, "VOYAGER":0, "NOTHING":0, "EXTREME":0, "EARTH":0, "CREDITS":0}

class SceneFailureCount(SessionFeature):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._failure_count : int = 0
        self._scene_started = False
        self._cnt_dict = scenes_map.copy()
        self._curr_scene = None
        self._scene_list = list()
        self._game_state = list()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        # return ["scene_change", "failed"]
        return ["scene_end", "scene_begin"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        # if event.EventName == "scene_change":
        #     self._scene_list.append(event.event_data.get("scene_name"))
        # elif event.EventName == "failed":
        #     self._curr_scene = self._scene_list[-1]
        #     self._cnt_dict[self._curr_scene] += 1
        self._game_state.append(event.game_state)
        # return

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        # return [self._cnt_dict]
        return [self._game_state]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "2"