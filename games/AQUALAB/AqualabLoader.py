# import standard libraries
import json
from typing import Any, Callable, Dict, List, Optional
# import local files
from extractors.detectors.Detector import Detector
from extractors.ExtractorLoader import ExtractorLoader
from extractors.features.Feature import Feature
from games.AQUALAB.detectors import *
from games.AQUALAB.features import *
from schemas.Event import Event
from schemas.GameSchema import GameSchema

EXPORT_PATH = "games/AQUALAB/DBExport.json"
CONFIG_PATH = "games/AQUALAB/AQUALAB.json"

## @class AqualabLoader
#  Extractor subclass for extracting features from Aqualab game data.
class AqualabLoader(ExtractorLoader):

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _loadFeature(self, feature_type:str, name:str, feature_args:Dict[str,Any], count_index:Optional[int] = None) -> Feature:
        ret_val : Feature
        if feature_type == "ActiveJobs":
            ret_val = ActiveJobs.ActiveJobs(name=name, description=feature_args["description"], job_map=self._job_map)
        elif feature_type == "EchoSessionID":
            ret_val = EchoSessionID.EchoSessionID(name=name, description=feature_args["description"])
        elif feature_type == "EventList":
            ret_val = EventList.EventList(name=name, description=feature_args["description"])
        elif feature_type == "JobActiveTime":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobActiveTime.JobActiveTime(name=name, description=feature_args["description"], job_num=count_index, job_map=self._job_map)
        elif feature_type == "JobArgumentationTime":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobArgumentationTime.JobArgumentationTime(name=name, description=feature_args["description"], job_num=count_index, job_map=self._job_map)
        elif feature_type == "JobCompletionTime":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobCompletionTime.JobCompletionTime(name=name, description=feature_args["description"], job_num=count_index, job_map=self._job_map)
        elif feature_type == "JobDiveSitesCount":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobDiveSitesCount.JobDiveSitesCount(name=name, description=feature_args["description"], job_num=count_index, job_map=self._job_map)
        elif feature_type == "JobDiveTime":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobDiveTime.JobDiveTime(name=name, description=feature_args["description"], job_num=count_index, job_map=self._job_map)
        elif feature_type == "JobExperimentationTime":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobExperimentationTime.JobExperimentationTime(name=name, description=feature_args["description"], job_num=count_index, job_map=self._job_map)
        elif feature_type == "JobGuideCount":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobGuideCount.JobGuideCount(name=name, description=feature_args["description"], job_num=count_index, job_map=self._job_map)
        elif feature_type == "JobHelpCount":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobHelpCount.JobHelpCount(name=name, description=feature_args["description"], job_num=count_index, job_map=self._job_map)
        elif feature_type == "JobModelingTime":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobModelingTime.JobModelingTime(name=name, description=feature_args["description"], job_num=count_index, job_map=self._job_map)
        elif feature_type == "JobTasksCompleted":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobTasksCompleted.JobTasksCompleted(name=name, description=feature_args["description"], job_num=count_index, job_map=self._job_map)
        elif feature_type == "JobsAttempted":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobsAttempted.JobsAttempted(name=name, description=feature_args["description"], job_num=count_index, job_map=self._job_map, diff_map=self._diff_map)
        elif feature_type == "JobsCompleted":
            ret_val = JobsCompleted.JobsCompleted(name=name, description=feature_args["description"], player_id=self._player_id)
        elif feature_type == "PlayerSummary":
            ret_val = PlayerSummary.PlayerSummary(name=name, description=feature_args["description"])
        elif feature_type == "PopulationSummary":
            ret_val = PopulationSummary.PopulationSummary(name=name, description=feature_args["description"])
        elif feature_type == "SessionDiveSitesCount":
            ret_val = SessionDiveSitesCount.SessionDiveSitesCount(name=name, description=feature_args["description"])
        elif feature_type == "SessionDuration":
            ret_val = SessionDuration.SessionDuration(name=name, description=feature_args["description"], session_id=self._session_id)
        elif feature_type == "SessionGuideCount":
            ret_val = SessionGuideCount.SessionGuideCount(name=name, description=feature_args["description"])
        elif feature_type == "SessionHelpCount":
            ret_val = SessionHelpCount.SessionHelpCount(name=name, description=feature_args["description"])
        elif feature_type == "SessionID":
            ret_val = SessionID.SessionID(name=name, description=feature_args["description"], session_id=self._session_id)
        elif feature_type == "SessionJobsCompleted":
            ret_val = SessionJobsCompleted.SessionJobsCompleted(name=name, description=feature_args["description"])
        elif feature_type == "SwitchJobsCount":
            ret_val = SwitchJobsCount.SwitchJobsCount(name=name, description=feature_args["description"])
        elif feature_type == "SyncCompletionTime":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = SyncCompletionTime.SyncCompletionTime(name=name, description=feature_args["description"])
        elif feature_type == "TopJobCompletionDestinations":
            ret_val = TopJobCompletionDestinations.TopJobCompletionDestinations(name=name, description=feature_args["description"], job_map=self._job_map)
        elif feature_type == "TopJobSwitchDestinations":
            ret_val = TopJobSwitchDestinations.TopJobSwitchDestinations(name=name, description=feature_args["description"], job_map=self._job_map)
        elif feature_type == "TotalArgumentationTime":
            ret_val = TotalArgumentationTime.TotalArgumentationTime(name=name, description=feature_args["description"])
        elif feature_type == "TotalDiveTime":
            ret_val = TotalDiveTime.TotalDiveTime(name=name, description=feature_args["description"])
        elif feature_type == "TotalExperimentationTime":
            ret_val = TotalExperimentationTime.TotalExperimentationTime(name=name, description=feature_args["description"])
        elif feature_type == "UserAvgSessionDuration":
            ret_val = UserAvgSessionDuration.UserAvgSessionDuration(name=name, description=feature_args["description"], player_id=self._player_id)
        elif feature_type == "UserSessionCount":
            ret_val = UserSessionCount.UserSessionCount(name=name, description=feature_args["description"], player_id=self._player_id)
        elif feature_type == "UserTotalSessionDuration":
            ret_val = UserTotalSessionDuration.UserTotalSessionDuration(name=name, description=feature_args["description"], player_id=self._player_id)
        else:
            raise NotImplementedError(f"'{feature_type}' is not a valid feature for Aqualab.")
        return ret_val

    def _loadDetector(self, detector_type:str, name:str, detector_args:Dict[str,Any], trigger_callback:Callable[[Event], None], count_index:Optional[int] = None) -> Detector:
        ret_val : Detector
        if detector_type == "CollectFactNoJob":
            ret_val = CollectFactNoJob.CollectFactNoJob(name=name, description=detector_args["description"], trigger_callback=trigger_callback)
        if detector_type == "DiveSiteNoEvidence":
            ret_val = DiveSiteNoEvidence.DiveSiteNoEvidence(name=name, description=detector_args["description"], trigger_callback=trigger_callback, threshold=detector_args['threshold'])
        elif detector_type == "EchoRoomChange":
            ret_val = EchoRoomChange.EchoRoomChange(name=name, description=detector_args["description"], trigger_callback=trigger_callback)
        else:
            raise NotImplementedError(f"'{detector_type}' is not a valid detector for Aqualab.")
        return ret_val

    # *** BUILT-INS ***

    ## Constructor for the AqualabLoader class.
    def __init__(self, player_id:str, session_id:str, game_schema: GameSchema, feature_overrides:Optional[List[str]]):
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
        super().__init__(player_id=player_id, session_id=session_id, game_schema=game_schema, feature_overrides=feature_overrides)
        self._job_map = {"no-active-job": 0}
        self._diff_map = {0: {"experimentation": 0, "modeling": 0, "argumentation": 0} }
        data = None

        # Load Aqualab jobs export and map job names to integer values
        with open(EXPORT_PATH, "r") as file:
            export = json.load(file)

            for i, job in enumerate(export["jobs"], start=1):
                self._job_map[job["id"]] = i
                self._diff_map[i] = job["difficulties"]

        # Update level count
        self._game_schema._max_level = len(self._job_map) - 1

    def getJobMap(self) -> Dict:
        return self._job_map
