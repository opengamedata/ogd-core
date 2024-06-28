## import standard libraries
import json
from typing import Any, Callable, Dict, Final, List, Optional
## import local files
from . import features
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.generators.extractors.Feature import Feature
from ogd.games.ICECUBE.features import *
# from ogd.games.ICECUBE.DBExport import scene_map
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.schemas.games.GameSchema import GameSchema
from ogd.core.utils.Logger import Logger

## @class WaveExtractor
#  Extractor subclass for extracting features from Waves game data.

EXPORT_PATH : Final[str] = "games/ICECUBE/DBExport.json"
class IcecubeLoader(GeneratorLoader):

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @staticmethod
    def _getFeaturesModule():
        return features
    
    def _loadFeature(self, feature_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any]) -> Optional[Feature]:
        ret_val : Optional[Feature] = None
        if extractor_params._count_index is None:
            match feature_type:
                case "ScenesEncountered":
                    ret_val = ScenesEncountered.ScenesEncountered(params=extractor_params)
                case "Session_Language":
                    ret_val = Session_Language.Session_Language(params=extractor_params)
                case "SessionDuration":
                    ret_val = SessionDuration.SessionDuration(params=extractor_params, session_id=self._session_id)
                case "HeadsetOnCount":
                    ret_val = HeadsetOnCount.HeadsetOnCount(params=extractor_params)
                case "ObjectSelectionsDuringVoiceover":
                    ret_val = ObjectSelectionsDuringVoiceover.ObjectSelectionsDuringVoiceover(params=extractor_params)
                case "SceneFailureCount":
                    ret_val = SceneFailureCount.SceneFailureCount(params=extractor_params)
                case _:
                    Logger.Log(f"'{feature_type}' is not a valid aggregate feature type for Icecube.")
        # Per-count features
        else:
            match feature_type:
                case "SceneFailures":
                    ret_val = SceneFailures.SceneFailures(params=extractor_params)
                case "TaskTimeToComplete":
                        ret_val = TaskTimeToComplete.TaskTimeToComplete(params=extractor_params)
                case "SceneDuration":
                        ret_val = SceneDuration.SceneDuration(params=extractor_params)
                case _:
                    Logger.Log(f"'{feature_type}' is not a valid aggregate feature for Icecube.")
            
        return ret_val

    def _loadDetector(self, detector_type:str, name:str, detector_args:Dict[str,Any], trigger_callback:Callable[[Event], None], count_index:Optional[int] = None) -> Optional[Detector]:
        Logger.Log(f"'{detector_type}' is not a valid detector for Waves.")
        return None

    # *** BUILT-INS & PROPERTIES ***

    ## Constructor for the WaveLoader class.
    def __init__(self, player_id:str, session_id: str, game_schema:GameSchema, mode:ExtractionMode, feature_overrides:Optional[List[str]]=None):
        """Constructor for the WaveLoader class.

        :param player_id: _description_
        :type player_id: str
        :param session_id: The id number for the session whose data is being processed by this instance
        :type session_id: str
        :param game_schema: A data structure containing information on how the game events and other data are structured
        :type game_schema: GameSchema
        :param feature_overrides: A list of features to export, overriding the default of exporting all enabled features.
        :type feature_overrides: Optional[List[str]]
        """
        super().__init__(player_id=player_id, session_id=session_id, game_schema=game_schema, mode=mode, feature_overrides=feature_overrides)
        self._scene_map = {"no-active-scene": 0}
        self._task_map = {}

        # Load Aqualab scenes export and map scene names to integer values
        # with open(EXPORT_PATH, "r") as file:
        #     export = json.load(file)

        #     task_num = 1
        #     for i, scene in enumerate(export["scenes"], start=1):
        #         self._scene_map[scene["id"]] = i
        #         self._diff_map[i] = scene["difficulties"]
        #         for task in scene["tasks"]:
        #             task_by_scene = scene["id"] + "_" + task["id"]
        #             self._task_map[task_by_scene] = task_num
        #             task_num += 1

        # Update level count
        # self._game_schema._max_level = len(self._scene_map) - 1