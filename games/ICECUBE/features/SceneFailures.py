# import libraries
import json
from typing import Any, List, Optional
# import local files
from extractors.Extractor import ExtractorParameters
from extractors.features.PerCountFeature import PerCountFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
from games.ICECUBE.DBExport import scene_map
from games.ICECUBE.features.PerSceneFeature import PerSceneFeature
from games.ICECUBE.DBExport import scenes_list
from utils import Logger

# import libraries
import logging

scenes_map = {"ICE":0, "VOYAGER":1, "NOTHING":2, "EXTREME":3, "EARTH":4, "CREDITS":5, "None":6}

class SceneFailures(PerCountFeature):

    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._failure_count = 0
        self._name = None
        self._found = False
        self._task_idx = 0
        self._idx = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["scene_begin","scene_end", "failed"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        # Logger.Log(f"event data is {event.EventData}")
        if event.EventName == "failed":
            self._failure_count += 1
        
        
        

    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._failure_count]

    # *** Optionally override public functions. ***
    def _validateEventCountIndex(self, event: Event):
        ret_val : bool = False

        # scene_data = event.EventData.get("scene_name")
        scene_data = event.game_state.get("scene_name")
        # Logger.Log(f"scene_data collected = {scene_data}")
        
        # if scene_data is None:
        #     scene_data = "None"
        #     ret_val = True
        
        if scene_data is not None:
            # Logger.Log(f"session_id is {event.SessionID}")
            # Logger.Log(f"event name is {event.event_name}")
            if scenes_map[scene_data] == self.CountIndex:
                # Logger.Log(f"count index is {self.CountIndex}")
                # Logger.Log(f"map index is {scenes_map[scene_data]}")
            # Logger.Log(f"scene_data is {scene_data}")
                ret_val = True
        
        # else:
        #     Logger.Log(f"Got invalid job_name data in {type(self).__name__}", logging.WARNING)

        return ret_val
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "2"