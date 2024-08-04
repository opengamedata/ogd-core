# import standard libraries
import itertools
import json
from pathlib import Path
from typing import Any, Callable, Dict, Final, List, Optional

# import local files
from ogd.games import BLOOM
from ogd.games.BLOOM.detectors import * 
from ogd.games.BLOOM.features import *
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.schemas.games.GameSchema import GameSchema
from ogd.core.utils.utils import loadJSONFile
from . import features

#EXPORT_PATH : Final[str] = "games/BLOOM/DBExport.json"

## @class BloomLoader
#  Extractor subclass for extracting features from Bloomlab game data.
class BloomLoader(GeneratorLoader):
    """Class for loading Bloom generator instances."""

    # *** BUILT-INS & PROPERTIES ***

    ## Constructor for the BloomlabLoader class.
    def __init__(self, player_id:str, session_id:str, game_schema: GameSchema, mode:ExtractionMode, feature_overrides:Optional[List[str]]):
        """Constructor for the BloomlabLoader class.

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

    # Load Bloomlab jobs export and map job names to integer values
    # _dbexport_path = Path(BLOOM.__file__) if Path(BLOOM.__file__).is_dir() else Path(BLOOM.__file__).parent
    # with open(_dbexport_path / "DBExport.json", "r") as file:
    # export = json.load(file)

   # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @staticmethod
    def _getFeaturesModule():
        return features

    def _loadFeature(self, feature_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any]) -> Optional[Feature]:
        ret_val : Optional[Feature]
        # First run through aggregate features
        if extractor_params._count_index == None:
            match feature_type:
                case "ActiveTime":
                    ret_val = ActiveTime.ActiveTime(params=extractor_params, idle_threshold=schema_args.get("threshold", 30))
                case "AverageActiveTime":
                    ret_val = AverageActiveTime.AverageActiveTime(params=extractor_params)
                case "BloomAlertCount":
                    ret_val = BloomAlertCount.BloomAlertCount(params=extractor_params)
                case "BuildCount":
                    ret_val = BuildCount.BuildCount(params=extractor_params)
                case "BuildingUnlockCount":
                    ret_val = BuildingUnlockCount.BuildingUnlockCount(params=extractor_params)
                case "FailCount":
                    ret_val = FailCount.FailCount(params=extractor_params)
                case "GameCompletionStatus":
                    ret_val = GameCompletionStatus.GameCompletionStatus(params=extractor_params)
                case "NumberOfSessionsPerPlayer":
                    ret_val = NumberOfSessionsPerPlayer.NumberOfSessionsPerPlayer(params=extractor_params)
                case "SucceededThroughFailure":
                    ret_val = SucceededThroughFailure.SucceededThroughFailure(params=extractor_params)
                case "CountyUnlockCount":
                    ret_val = CountyUnlockCount.CountyUnlockCount(params=extractor_params)
                case _:
                    ret_val = None
        # then run through per-count features.
        else:
            match feature_type:
                case "CountyBloomAlertCount":
                    ret_val = CountyBloomAlertCount.CountyBloomAlertCount(params=extractor_params)
                case "CountyBuildCount":
                    ret_val = CountyBuildCount.CountyBuildCount(params=extractor_params)
                case "CountyFinalPolicySettings":
                    ret_val = CountyFinalPolicySettings.CountyFinalPolicySettings(params=extractor_params)
                case "CountyLatestMoney":
                    ret_val = CountyLatestMoney.CountyLatestMoney(params=extractor_params)
                case _:
                    ret_val = None
                
        return ret_val

    def _loadDetector(self, detector_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any], trigger_callback:Callable[[Event], None]) -> Detector:
        ret_val : Detector
        match detector_type:
            case _:
                raise NotImplementedError(f"'{detector_type}' is not a valid detector for Bloom.")
        return ret_val

    # @staticmethod
    # def GetBloomLabCount(db_export_path:Path=Path(".") / "ogd" / "games" / "BLOOM"):
    #     db_export = loadJSONFile(filename="DBExport.json", path=db_export_path)
    #     return len(db_export.get("jobs", []))

    # @staticmethod
    # def GetBloomTaskCount(db_export_path:Path=Path(".") / "ogd" / "games" / "BLOOM"):
    #     db_export = loadJSONFile(filename="DBExport.json", path=db_export_path)
    #     list_o_lists = [job.get('tasks', []) for job in db_export.get('jobs', [])]
    #     # jobs_to_task_cts = [f"{job.get('id')}: {len(job.get('tasks', []))}" for job in db_export.get('jobs', [])]
    #     # Logger.Log(f"Task counts by job:\n{jobs_to_task_cts}", logging.DEBUG)
    #     all_tasks    = list(itertools.chain.from_iterable(list_o_lists))
    #     return len(all_tasks)
