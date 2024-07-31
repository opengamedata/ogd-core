# import standard libraries
import itertools
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
# import local files
from . import features
from ogd.games import THERMOVR
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.generators.extractors.Feature import Feature
from ogd.games.THERMOVR.detectors import *
from ogd.games.THERMOVR.features import *
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.schemas.games.GameSchema import GameSchema
from ogd.core.utils.utils import loadJSONFile
from ogd.core.utils.Logger import Logger

EXPORT_PATH = "games/THERMOVR/DBExport.json"

## @class ThermoVRLoader
#  Extractor subclass for extracting features from ThermoVR game data.
class ThermoVRLoader(GeneratorLoader):

    # *** BUILT-INS & PROPERTIES ***

    ## Constructor for the ThermoVRLoader class.
    def __init__(self, player_id:str, session_id:str, game_schema: GameSchema, mode:ExtractionMode, feature_overrides:Optional[List[str]]):
        """Constructor for the ThermoVRLoader class.

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
        self._lab_map = {}
        data = None

        # Load ThermoVR jobs export and map job names to integer values
        _dbexport_path = Path(THERMOVR.__file__) if Path(THERMOVR.__file__).is_dir() else Path(THERMOVR.__file__).parent
        with open(_dbexport_path / "DBExport.json", "r") as file:
            export = json.load(file)

            # task_num = 1
            # for i, lab in enumerate(export["labs"], start=1):
            #     self._lab_map[lab["id"]] = i
            #     for task in lab["tasks"]:
            #         task_by_lab = lab["id"] + "_" + task["id"]
            #         self._task_map[task_by_lab] = task_num
            #         task_num += 1

        # Update level count
        self._game_schema._max_level = len(self._lab_map) - 1

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @staticmethod
    def _getFeaturesModule():
        return features

    def _loadFeature(self, feature_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any]) -> Optional[Feature]:
        ret_val : Optional[Feature] = None
        # First run through aggregate features
        if extractor_params._count_index == None:
            match feature_type:
                case "PhasesReached":
                    ret_val = PhasesReached.PhasesReached(params=extractor_params)
                case "PlayMode":
                    ret_val = PlayMode.PlayMode(params=extractor_params)
                case "TaskCompleteCount":
                    ret_val = TaskCompleteCount.TaskCompleteCount(params=extractor_params)
                case "LabCompleteCount":
                    ret_val = LabCompleteCount.LabCompleteCount(params=extractor_params)
                case "LeftHandMoves":
                    ret_val = LeftHandMoves.LeftHandMoves(params=extractor_params)
                case "RightHandMoves":
                    ret_val = RightHandMoves.RightHandMoves(params=extractor_params)
                case "ToolNudgeCount":
                    ret_val = ToolNudgeCount.ToolNudgeCount(params=extractor_params)
                case "ToolSliderTime":
                    ret_val = ToolSliderTime.ToolSliderTime(params=extractor_params)
                case _:
                    Logger.Log(f"'{feature_type}' is not a valid aggregate feature type for ThermoVR.")
        # then run through per-count features.
        else:
            match feature_type:
                case _:
                    Logger.Log(f"'{feature_type}' is not a valid per-count feature type for ThermoVR.")
        return ret_val

    def _loadDetector(self, detector_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any], trigger_callback:Callable[[Event], None]) -> Optional[Detector]:
        ret_val : Optional[Detector] = None
        match detector_type:
            case _:
                Logger.Log(f"'{detector_type}' is not a valid detector for ThermoVR.")
        return ret_val

    # @staticmethod
    # def GetThermoVRLabCount(db_export_path:Path=Path(".") / "ogd" / "games" / "THERMOVR"):
    #     db_export = loadJSONFile(filename="DBExport.json", path=db_export_path)
    #     return len(db_export.get("jobs", []))

    # @staticmethod
    # def GetThermoVRTaskCount(db_export_path:Path=Path(".") / "ogd" / "games" / "THERMOVR"):
    #     db_export = loadJSONFile(filename="DBExport.json", path=db_export_path)
    #     list_o_lists = [job.get('tasks', []) for job in db_export.get('jobs', [])]
    #     # jobs_to_task_cts = [f"{job.get('id')}: {len(job.get('tasks', []))}" for job in db_export.get('jobs', [])]
    #     # Logger.Log(f"Task counts by job:\n{jobs_to_task_cts}", logging.DEBUG)
    #     all_tasks    = list(itertools.chain.from_iterable(list_o_lists))
    #     return len(all_tasks)
