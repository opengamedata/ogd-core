# import standard libraries
from datetime import timedelta
from pathlib import Path
from typing import Any, Callable, Dict, Final, List, Optional

# import local files
from ogd.games import BLOOM
from ogd.games.BLOOM.detectors import * 
from ogd.games.BLOOM.features import *
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.configs.generators.GeneratorCollectionConfig import GeneratorCollectionConfig
from ogd.common.utils.fileio import loadJSONFile
from ogd.games.BLOOM.features import PersistThroughFailure
from . import features

# EXPORT_PATH : Final[str] = "games/BLOOM/DBExport.json"

## @class BloomLoader
#  Extractor subclass for extracting features from Bloomlab game data.
class BloomLoader(GeneratorLoader):
    """Class for loading Bloom generator instances."""

    # *** BUILT-INS & PROPERTIES ***

    ## Constructor for the BloomlabLoader class.
    def __init__(self, player_id:str, session_id:str, generator_config: GeneratorCollectionConfig, mode:ExtractionMode, feature_overrides:Optional[List[str]]):
        """Constructor for the BloomlabLoader class.

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

    # Load Bloomlab jobs export and map job names to integer values
    # _dbexport_path = Path(BLOOM.__file__) if Path(BLOOM.__file__).is_dir() else Path(BLOOM.__file__).parent
    # with open(_dbexport_path / "DBExport.json", "r") as file:
    # export = json.load(file)

   # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @staticmethod
    def _getFeaturesModule():
        return features
    
    def _loadFeature(self, feature_type: str, extractor_params: GeneratorParameters, schema_args: Dict[str, Any]) -> Optional[Extractor]:
        ret_val: Optional[Extractor] = None

        # First run through aggregate features
        if extractor_params._count_index is None:
            match feature_type:
                case "ActiveTime":
                    ret_val = ActiveTime.ActiveTime(params=extractor_params, idle_threshold=schema_args.get("threshold", 30))
                case "AlertCount":
                    ret_val = AlertCount.AlertCount(params=extractor_params)
                case "ActiveCounties":
                    ret_val = ActiveCounties.ActiveCounties(params=extractor_params)
                case "AlertResponseCount":
                    ret_val = AlertResponseCount.AlertResponseCount(params=extractor_params)
                case "AlertReviewCount":
                    ret_val = AlertReviewCount.AlertReviewCount(params=extractor_params)
                case "AverageActiveTime":
                    ret_val = AverageActiveTime.AverageActiveTime(params=extractor_params)
                case "AverageBuildingInspectTime":
                    ret_val = AverageBuildingInspectTime.AverageBuildingInspectTime(params=extractor_params)
                case "AverageEconomyViewTime":
                    ret_val = AverageEconomyViewTime.AverageEconomyViewTime(params=extractor_params)
                case "AveragePhosphorusViewTime":
                    ret_val = AveragePhosphorusViewTime.AveragePhosphorusViewTime(params=extractor_params)
                case "BloomAlertCount":
                    ret_val = BloomAlertCount.BloomAlertCount(params=extractor_params)
                case "BuildingUnlockCount":
                    ret_val = BuildingUnlockCount.BuildingUnlockCount(params=extractor_params)
                case "EconomyViewUnlocked":
                    ret_val = EconomyViewUnlocked.EconomyViewUnlocked(params=extractor_params)
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
                case "PersistThroughFailure":
                    ret_val = PersistThroughFailure.PersistThroughFailure(params=extractor_params)
                case "PersistenceTime":
                    ret_val = PersistenceTime.PersistenceTime(params=extractor_params)
                case "PhosphorusViewUnlocked":
                    ret_val = PhosphorusViewUnlocked.PhosphorusViewUnlocked(params=extractor_params)
                case "PlayerSummary":
                    ret_val = PlayerSummary.PlayerSummary(params=extractor_params)
                case "PopulationSummary":
                    ret_val = PopulationSummary.PopulationSummary(params=extractor_params)
                case "PolicyUnlocked":
                    ret_val = PolicyUnlocked.PolicyUnlocked(params=extractor_params)
                case "QuitOnBloomFail":
                    ret_val = QuitOnBloomFail.QuitOnBloomFail(params=extractor_params)
                case "QuitOnCityFail":
                    ret_val = QuitOnCityFail.QuitOnCityFail(params=extractor_params)
                case "QuitOnBankruptcy":
                    ret_val = QuitOnBankruptcy.QuitOnBankruptcy(params=extractor_params)
                case "TopCountySwitchDestinations":
                    ret_val = TopCountySwitchDestinations.TopCountySwitchDestinations(params=extractor_params)
                case "TopCountyCompletionDestinations":
                    ret_val = TopCountyCompletionDestinations.TopCountyCompletionDestinations(params=extractor_params)
                case "BuildingInspectorTabCount": 
                    ret_val = BuildingInspectorTabCount.BuildingInspectorTabCount(params=extractor_params)
                case "GoodPolicyCount":
                    ret_val = GoodPolicyCount.GoodPolicyCount(params=extractor_params)
                # case "PhosphorusViewTime":
                #     ret_val = PhosphorusViewTime.PhosphorusViewTime(params=extractor_params)
                # case "InspectorResponseCount":
                #     ret_val = InspectorResponseCount.InspectorResponseCount(params=extractor_params)
                case _:
                    ret_val = None

        # Then run through per-county features.
        else:
            match feature_type:
                case "CountyUnlockTime":
                    ret_val = CountyUnlockTime.CountyUnlockTime(params=extractor_params)
                case "CountyBloomAlertCount":
                    ret_val = CountyBloomAlertCount.CountyBloomAlertCount(params=extractor_params)
                case "CountyBuildCount":
                    ret_val = CountyBuildCount.CountyBuildCount(params=extractor_params)
                case "CountyFailCount":
                    ret_val = CountyFailCount.CountyFailCount(params=extractor_params)
                case "CountyFinalPolicySettings":
                    ret_val = CountyFinalPolicySettings.CountyFinalPolicySettings(params=extractor_params)
                case "CountyLatestMoney":
                    ret_val = CountyLatestMoney.CountyLatestMoney(params=extractor_params)
                case "CountyPolicyChangeCount":
                    ret_val = CountyPolicyChangeCount.CountyPolicyChangeCount(params=extractor_params)
                
                case "JobsAttempted":
                    ret_val = JobsAttempted.JobsAttempted(params=extractor_params)
                    
                case _:
                    ret_val = None

        return ret_val

    def _loadDetector(self, detector_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any], trigger_callback:Callable[[Event], None]) -> Detector:
        ret_val : Detector
        match detector_type:
            case "AlertClickThrough":
                _max_rate = schema_args.get("max_rate", AlertClickThrough.AlertClickThrough.DEFAULT_MAX_RATE)
                ret_val = AlertClickThrough.AlertClickThrough(params=extractor_params, trigger_callback=trigger_callback, max_reading_rate=_max_rate)
            case "AlertFollowedByInspect":
                _inspect_threshold = timedelta(seconds=schema_args.get("threshold", 15))
                ret_val = AlertFollowedByInspect.AlertFollowedByInspect(params=extractor_params, trigger_callback=trigger_callback, inspect_time_threshold=_inspect_threshold)
            case "AlertFollowedByPolicy":
                _policy_threshold = timedelta(seconds=schema_args.get("threshold", 30))
                ret_val = AlertFollowedByPolicy.AlertFollowedByPolicy(params=extractor_params, trigger_callback=trigger_callback, policy_time_threshold=_policy_threshold)
            case "CutsceneClickThrough":
                _max_rate = schema_args.get("max_rate", CutsceneClickThrough.CutsceneClickThrough.DEFAULT_MAX_RATE)
                ret_val = CutsceneClickThrough.CutsceneClickThrough(params=extractor_params, trigger_callback=trigger_callback, max_reading_rate=_max_rate)
            case "GoodPolicyCombo":
                _budget_threshold = schema_args.get("threshold", 150)
                ret_val = GoodPolicyCombo.GoodPolicyCombo(params=extractor_params, trigger_callback=trigger_callback, surplus_budget_threshold=_budget_threshold)
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
