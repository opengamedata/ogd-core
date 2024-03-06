# import standard libraries
import itertools
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
# import local files
import games.AQUALAB.features
from extractors.detectors.Detector import Detector
from extractors.Extractor import ExtractorParameters
from extractors.ExtractorLoader import ExtractorLoader
from extractors.features.Feature import Feature
from games.AQUALAB.detectors import *
from games.AQUALAB.features import *
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.games.GameSchema import GameSchema
from utils.utils import loadJSONFile

EXPORT_PATH = "games/AQUALAB/DBExport.json"

## @class AqualabLoader
#  Extractor subclass for extracting features from Aqualab game data.
class AqualabLoader(ExtractorLoader):

    # *** BUILT-INS & PROPERTIES ***

    ## Constructor for the AqualabLoader class.
    def __init__(self, player_id:str, session_id:str, game_schema: GameSchema, mode:ExtractionMode, feature_overrides:Optional[List[str]]):
        """Constructor for the AqualabLoader class.

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
        self._job_map = {"no-active-job": 0}
        self._diff_map = {0: {"experimentation": 0, "modeling": 0, "argumentation": 0} }
        self._task_map = {}
        data = None

        # Load Aqualab jobs export and map job names to integer values
        with open(EXPORT_PATH, "r") as file:
            export = json.load(file)

            task_num = 1
            for i, job in enumerate(export["jobs"], start=1):
                self._job_map[job["id"]] = i
                self._diff_map[i] = job["difficulties"]
                for task in job["tasks"]:
                    task_by_job = job["id"] + "_" + task["id"]
                    self._task_map[task_by_job] = task_num
                    task_num += 1

        # Update level count
        self._game_schema._max_level = len(self._job_map) - 1

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @staticmethod
    def _getFeaturesModule():
        return games.AQUALAB.features

    def _loadFeature(self, feature_type:str, extractor_params:ExtractorParameters, schema_args:Dict[str,Any]) -> Feature:
        ret_val : Feature
        # First run through aggregate features
        if feature_type == "ActiveTime":
            ret_val = ActiveTime.ActiveTime(params=extractor_params, job_map=self._job_map, active_threads=schema_args.get("Active_threshold"))
        elif feature_type == "JobPlayTime":
            ret_val = ActiveTime.ActiveTime(params=extractor_params, job_map=self._job_map, active_threads=schema_args.get("Active_threshold"))
        elif feature_type == "JobTriesInArgument":
            ret_val = JobTriesInArgument.JobTriesInArgument(params=extractor_params, job_map=self._job_map)
        elif feature_type == "ModelInterveneCount":
            ret_val = ModelInterveneCount.ModelInterveneCount(params=extractor_params, job_map=self._job_map)
        elif feature_type == "TankRulesCount":
            ret_val = TankRulesCount.TankRulesCount(params=extractor_params)
        elif feature_type == "ModelExportCount":
            ret_val = ModelExportCount.ModelExportCount(params=extractor_params, job_map=self._job_map)
        elif feature_type == "ModelPredictCount":
            ret_val = ModelPredictCount.ModelPredictCount(params=extractor_params, job_map=self._job_map)
        elif feature_type == "UserAvgActiveTime":
            ret_val = UserAvgActiveTime.UserAvgActiveTime(
                params=extractor_params, player_id=self._player_id)
        elif feature_type == "ActiveJobs":
            ret_val = ActiveJobs.ActiveJobs(params=extractor_params, job_map=self._job_map)
        elif feature_type == "AverageSessionTime":
            ret_val = AverageSessionTime.AverageSessionTime(params=extractor_params)
        elif feature_type == "EchoSessionID":
            ret_val = EchoSessionID.EchoSessionID(params=extractor_params)
        elif feature_type == "EventList":
            ret_val = EventList.EventList(params=extractor_params)
        elif feature_type == "JobsCompleted":
            ret_val = JobsCompleted.JobsCompleted(params=extractor_params, player_id=self._player_id)
        elif feature_type == "PlayerSummary":
            ret_val = PlayerSummary.PlayerSummary(params=extractor_params)
        elif feature_type == "PopulationSummary":
            ret_val = PopulationSummary.PopulationSummary(params=extractor_params)
        elif feature_type == "RegionJobCount":
            ret_val = RegionJobCount.RegionJobCount(params=extractor_params)
        elif feature_type == "RegionName":
            ret_val = RegionName.RegionName(params=extractor_params)
        elif feature_type == "SessionDiveSitesCount":
            ret_val = SessionDiveSitesCount.SessionDiveSitesCount(params=extractor_params)
        elif feature_type == "SessionDuration":
            ret_val = SessionDuration.SessionDuration(params=extractor_params, threshold=int)
        elif feature_type == "TotalHelpCount":
            ret_val = TotalHelpCount.TotalHelpCount(params=extractor_params)
        elif feature_type == "SessionID":
            ret_val = SessionID.SessionID(params=extractor_params, session_id=self._session_id)
        elif feature_type == "SwitchJobsCount":
            ret_val = SwitchJobsCount.SwitchJobsCount(params=extractor_params)
        elif feature_type == "TopJobCompletionDestinations":
            ret_val = TopJobCompletionDestinations.TopJobCompletionDestinations(params=extractor_params, job_map=self._job_map)
        elif feature_type == "TopJobSwitchDestinations":
            ret_val = TopJobSwitchDestinations.TopJobSwitchDestinations(params=extractor_params, job_map=self._job_map)
        elif feature_type == "TotalArgumentationTime":
            ret_val = TotalArgumentationTime.TotalArgumentationTime(params=extractor_params)
        elif feature_type == "TotalDiveTime":
            ret_val = TotalDiveTime.TotalDiveTime(params=extractor_params)
        elif feature_type == "TotalExperimentationTime":
            ret_val = TotalExperimentationTime.TotalExperimentationTime(params=extractor_params)
        elif feature_type == "TotalModelingTime":
            ret_val = TotalModelingTime.TotalModelingTime(params=extractor_params)
        elif feature_type == "TotalGuideCount":
            ret_val = TotalGuideCount.TotalGuideCount(params=extractor_params)
        elif feature_type == "TotalPlayTime":
            ret_val = TotalPlayTime.TotalPlayTime(params=extractor_params)
        elif feature_type == "PlayLocations":
            ret_val = PlayLocations.PlayLocations(params=extractor_params)
        elif feature_type == "UserAvgSessionDuration":
            ret_val = UserAvgSessionDuration.UserAvgSessionDuration(params=extractor_params, player_id=self._player_id)
        elif feature_type == "UserTotalSessionDuration":
            ret_val = UserTotalSessionDuration.UserTotalSessionDuration(params=extractor_params, player_id=self._player_id)
        # then run through per-count features.
        elif extractor_params._count_index is not None:
            if feature_type == "JobActiveTime":
                ret_val = JobActiveTime.JobActiveTime(params=extractor_params, job_map=self._job_map)
            elif feature_type == "JobArgumentation":
                ret_val = JobArgumentation.JobArgumentation(params=extractor_params, job_map=self._job_map)
            elif feature_type == "JobCompletionTime":
                ret_val = JobCompletionTime.JobCompletionTime(params=extractor_params, job_map=self._job_map)
            elif feature_type == "JobDiveSitesCount":
                ret_val = JobDiveSitesCount.JobDiveSitesCount(params=extractor_params, job_map=self._job_map)
            elif feature_type == "JobDiveTime":
                ret_val = JobDiveTime.JobDiveTime(params=extractor_params, job_map=self._job_map)
            elif feature_type == "JobExperimentation":
                ret_val = JobExperimentation.JobExperimentation(params=extractor_params, job_map=self._job_map)
            elif feature_type == "JobGuideCount":
                ret_val = JobGuideCount.JobGuideCount(params=extractor_params, job_map=self._job_map)
            elif feature_type == "JobHelpCount":
                ret_val = JobHelpCount.JobHelpCount(params=extractor_params, job_map=self._job_map)
            elif feature_type == "JobLocationChanges":
                ret_val = JobLocationChanges.JobLocationChanges(params=extractor_params, job_map=self._job_map)
            elif feature_type == "JobModeling":
                ret_val = JobModeling.JobModeling(params=extractor_params, job_map=self._job_map)
            elif feature_type == "JobStartCount":
                ret_val = JobStartCount.JobStartCount(params=extractor_params, job_map=self._job_map)
            elif feature_type == "JobTasksCompleted":
                ret_val = JobTasksCompleted.JobTasksCompleted(params=extractor_params, job_map=self._job_map)
            elif feature_type == "JobsAttempted":
                ret_val = JobsAttempted.JobsAttempted(params=extractor_params, job_map=self._job_map, diff_map=self._diff_map)
            elif feature_type == "SyncCompletionTime":
                ret_val = SyncCompletionTime.SyncCompletionTime(params=extractor_params)
            elif feature_type == "JobPriorComplete":
                ret_val = JobPriorComplete.JobPriorComplete(params=extractor_params, job_map=self._job_map)
            elif feature_type == "JobPriorAttempt":
                ret_val = JobPriorAttempt.JobPriorAttempt(params=extractor_params, job_map=self._job_map)
            else:
                raise NotImplementedError(f"'{feature_type}' is not a valid feature type for Aqualab.")
        else:
            raise TypeError(f"Got None for extractor_params._count_index (feature_type={feature_type}), should have a value!")
        return ret_val

    def _loadDetector(self, detector_type:str, extractor_params:ExtractorParameters, schema_args:Dict[str,Any], trigger_callback:Callable[[Event], None]) -> Detector:
        ret_val : Detector
        if detector_type == "CollectFactNoJob":
            ret_val = CollectFactNoJob.CollectFactNoJob(params=extractor_params, trigger_callback=trigger_callback)
        elif detector_type == "DiveSiteNoEvidence":
            ret_val = DiveSiteNoEvidence.DiveSiteNoEvidence(params=extractor_params, trigger_callback=trigger_callback, threshold=schema_args['threshold'])
        elif detector_type == "EchoRoomChange":
            ret_val = EchoRoomChange.EchoRoomChange(params=extractor_params, trigger_callback=trigger_callback)
        elif detector_type == "Idle":
            ret_val = Idle.Idle(params=extractor_params, trigger_callback=trigger_callback, idle_level=schema_args.get("idle_level"))
        elif detector_type == "SceneChangeFrequently":
            ret_val = SceneChangeFrequently.SceneChangeFrequently(params=extractor_params, trigger_callback=trigger_callback, time_threshold=schema_args.get("threshold"))
        elif detector_type == "HintAndLeave":
            ret_val = HintAndLeave.HintAndLeave(params=extractor_params, trigger_callback=trigger_callback, time_threshold=schema_args.get("threshold"))
        elif detector_type == "TwoHints":
            ret_val = TwoHints.TwoHints(params=extractor_params, trigger_callback=trigger_callback, time_threshold=schema_args.get("threshold"))
        else:
            raise NotImplementedError(f"'{detector_type}' is not a valid detector for Aqualab.")
        return ret_val

    @property
    def JobMap(self) -> Dict:
        return self._job_map

    @staticmethod
    def GetAqualabJobCount(db_export_path:Path=Path("./games/AQUALAB/")):
        db_export = loadJSONFile(filename="DBExport.json", path=db_export_path)
        return len(db_export.get("jobs", []))

    @staticmethod
    def GetAqualabTaskCount(db_export_path:Path=Path("./games/AQUALAB/")):
        db_export = loadJSONFile(filename="DBExport.json", path=db_export_path)
        list_o_lists = [job.get('tasks', []) for job in db_export.get('jobs', [])]
        # jobs_to_task_cts = [f"{job.get('id')}: {len(job.get('tasks', []))}" for job in db_export.get('jobs', [])]
        # Logger.Log(f"Task counts by job:\n{jobs_to_task_cts}", logging.DEBUG)
        all_tasks    = list(itertools.chain.from_iterable(list_o_lists))
        return len(all_tasks)
