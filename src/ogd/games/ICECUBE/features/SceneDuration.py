# import libraries
import json
from typing import Any, List, Optional
# import local files
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.games.ICECUBE.DBExport import scene_map
from ogd.games.ICECUBE.features.PerSceneFeature import PerSceneFeature
from ogd.games.ICECUBE.DBExport import scenes_list
from ogd.core.utils.Logger import Logger
from datetime import timedelta

# import libraries
import logging

scenes_map = {"ICE":0, "VOYAGER":1, "NOTHING":2, "EXTREME":3, "EARTH":4, "CREDITS":5, "None":6}

class SceneDuration(PerCountFeature):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._session_id = None
        self._scene_start_time = None
        self._prev_timestamp = None
        self._time = 0
        self._name = None
    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["scene_begin","scene_end"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if event.SessionID != self._session_id:
            self._session_id = event.SessionID

            if self._scene_start_time and self._prev_timestamp:
                self._time += (self._prev_timestamp - self._scene_start_time).total_seconds()
                self._scene_start_time = event.Timestamp

        
        if event.EventName == "scene_begin":
            self._scene_start_time = event.Timestamp
        elif event.EventName == "scene_end":
            if self._scene_start_time is not None:
                self._time += (event.Timestamp - self._scene_start_time).total_seconds()
                self._scene_start_time = None

        self._prev_timestamp = event.Timestamp

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [timedelta(seconds=self._time)]

    # *** Optionally override public functions. ***
    def _validateEventCountIndex(self, event: Event):
        ret_val : bool = False

        scene_data = event.game_state.get("scene_name")
        # if scene_data in scenes_map and scenes_map[scene_data] == self.CountIndex:
        #         ret_val = True
        if scene_data is not None:
            if scene_data in scenes_map and scenes_map[scene_data] == self.CountIndex:
                ret_val = True
        else:
            self.WarningMessage(f"Got invalid scene data in {type(self).__name__}")

        return ret_val
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "2"