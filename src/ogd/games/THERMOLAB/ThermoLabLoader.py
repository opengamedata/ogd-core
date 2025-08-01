# import standard libraries
import itertools
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
# OGD imports
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.configs.generators.GeneratorCollectionConfig import GeneratorCollectionConfig
from ogd.common.utils.utils import loadJSONFile
from ogd.common.utils.Logger import Logger
# import local files
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.games import THERMOLAB
from ogd.games.THERMOLAB.detectors import *
from ogd.games.THERMOLAB.features import *
from . import features

EXPORT_PATH = "games/THERMOLAB/DBExport.json"

## @class ThermoLabLoader
#  Extractor subclass for extracting features from ThermoLab game data.
class ThermoLabLoader(GeneratorLoader):

    # *** BUILT-INS & PROPERTIES ***

    ## Constructor for the ThermoLabLoader class.
    def __init__(self, player_id:str, session_id:str, generator_config: GeneratorCollectionConfig, mode:ExtractionMode, feature_overrides:Optional[List[str]]):
        """Constructor for the ThermoLabLoader class.

        :param player_id: _description_
        :type player_id: str
        :param session_id: The id number for the session whose data is being processed by this instance
        :type session_id: str
        :param generator_config: A data structure containing information on how the game events and other data are structured
        :type generator_config: GeneratorCollectionConfig
        :param feature_overrides: A list of features to export, overriding the default of exporting all enabled features.
        :type feature_overrides: Optional[List[str]]
        """
        super().__init__(player_id=player_id, session_id=session_id, generator_config=generator_config, mode=mode, feature_overrides=feature_overrides)
        self._lab_map = {}
        data = None

        # Load ThermoLab jobs export and map job names to integer values
        _dbexport_path = Path(THERMOLAB.__file__) if Path(THERMOLAB.__file__).is_dir() else Path(THERMOLAB.__file__).parent
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
        # self._generator_config._max_level = len(self._lab_map) - 1

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @staticmethod
    def _getFeaturesModule():
        return features

    def _loadFeature(self, feature_type: str, extractor_params: GeneratorParameters, schema_args: Dict[str, Any]) -> Optional[Extractor]:
        ret_val: Optional[Extractor] = None
        # First run through aggregate features
        if extractor_params._count_index is None:
            match feature_type:
                case "PhasesReached":
                    ret_val = PhasesReached.PhasesReached(params=extractor_params)
                case "PlayMode":
                    ret_val = PlayMode.PlayMode(params=extractor_params)
                case "TaskCompleteCount":
                    ret_val = TaskCompleteCount.TaskCompleteCount(params=extractor_params)
                case "LabCompleteCount":
                    ret_val = LabCompleteCount.LabCompleteCount(params=extractor_params)
                case "SectionCompleteCount":
                    ret_val = SectionCompleteCount.SectionCompleteCount(params=extractor_params)
                case "TotalPlayTime":
                    ret_val = TotalPlayTime.TotalPlayTime(params=extractor_params)
                case "AnswerAttemptsCount":
                    ret_val = AnswerAttemptsCount.AnswerAttemptsCount(params=extractor_params)
                case "CorrectAnswerOnFirstGuess":
                    ret_val = CorrectAnswerOnFirstGuess.CorrectAnswerOnFirstGuess(params=extractor_params)
                case "LeftHandMoves":
                    ret_val = LeftHandMoves.LeftHandMovesCount(params=extractor_params)
                case "RightHandMoves":
                    ret_val = RightHandMoves.RightHandMovesCount(params=extractor_params)
                case "ToolNudgeCount":
                    ret_val = ToolNudgeCount.ToolNudgeCount(params=extractor_params)
                case "ToolSliderTime":
                    ret_val = ToolSliderTime.ToolSliderTime(params=extractor_params)
                case _:
                    Logger.Log(f"'{feature_type}' is not a valid aggregate feature type for ThermoLab.")
        # then run through per-count features.
        else:
            match feature_type:
                case _:
                    Logger.Log(f"'{feature_type}' is not a valid per-count feature type for ThermoLab.")
        return ret_val

    def _loadDetector(self, detector_type: str, extractor_params: GeneratorParameters, schema_args: Dict[str, Any], trigger_callback: Callable[[Event], None]) -> Optional[Detector]:
        ret_val: Optional[Detector] = None
        match detector_type:
            case "player_move":
                ret_val = player_move.player_move(params=extractor_params, trigger_callback=trigger_callback)
            case _:
                Logger.Log(f"'{detector_type}' is not a valid detector for ThermoLab.")
        return ret_val

    # @staticmethod
    # def GetThermoLabLabCount(db_export_path:Path=Path(".") / "ogd" / "games" / "THERMOLAB"):
    #     db_export = loadJSONFile(filename="DBExport.json", path=db_export_path)
    #     return len(db_export.get("jobs", []))

    # @staticmethod
    # def GetThermoLabTaskCount(db_export_path:Path=Path(".") / "ogd" / "games" / "THERMOLAB"):
    #     db_export = loadJSONFile(filename="DBExport.json", path=db_export_path)
    #     list_o_lists = [job.get('tasks', []) for job in db_export.get('jobs', [])]
    #     # jobs_to_task_cts = [f"{job.get('id')}: {len(job.get('tasks', []))}" for job in db_export.get('jobs', [])]
    #     # Logger.Log(f"Task counts by job:\n{jobs_to_task_cts}", logging.DEBUG)
    #     all_tasks    = list(itertools.chain.from_iterable(list_o_lists))
    #     return len(all_tasks)
