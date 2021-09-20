## import standard libraries
import logging
import numpy as np
import typing
import traceback
from datetime import datetime
from sklearn.linear_model import LinearRegression
from typing import Any, Dict, List, Union
## import local files
from games.AQUALAB.extractors import *
import utils
from extractors.Extractor import Extractor
from extractors.Feature import Feature
from schemas.GameSchema import GameSchema

## @class WaveExtractor
#  Extractor subclass for extracting features from Waves game data.
class AqualabExtractor(Extractor):
    ## Constructor for the WaveExtractor class.
    #  Initializes some custom private data (not present in base class) for use
    #  when calculating some features.
    #  Sets the sessionID feature.
    #  Further, initializes all Q&A features to -1, representing unanswered questions.
    #
    #  @param session_id The id number for the session whose data is being processed
    #                    by this extractor instance.
    #  @param game_table A data structure containing information on how the db
    #                    table assiciated with this game is structured. 
    #  @param game_schema A dictionary that defines how the game data itself is
    #                     structured.
    def __init__(self, session_id: str, game_schema: GameSchema):
        self._game_schema = game_schema
        super().__init__(session_id=session_id, game_schema=game_schema)

    def _loadFeature(self, feature_type:str, name:str, feature_args:Dict[str,Any], count_index:Union[int,None] = None) -> Feature:
        ret_val : Feature
        if feature_type == "JobArgumentationTime":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobArgumentationTime.JobArgumentationTime(name=name, description=feature_args["description"], job_num=count_index, job_map=self._game_schema["job_map"])
        elif feature_type == "JobCompleteCount":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobCompleteCount.JobCompleteCount(name=name, description=feature_args["description"], job_num=count_index, job_map=self._game_schema["job_map"])
        elif feature_type == "JobCompletionTime":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobCompletionTime.JobCompletionTime(name=name, description=feature_args["description"], job_num=count_index, job_map=self._game_schema["job_map"])
        elif feature_type == "JobDiveSitesCount":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobDiveSitesCount.JobDiveSitesCount(name=name, description=feature_args["description"], job_num=count_index, job_map=self._game_schema["job_map"])
        elif feature_type == "JobDiveTime":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobDiveTime.JobDiveTime(name=name, description=feature_args["description"], job_num=count_index, job_map=self._game_schema["job_map"])
        elif feature_type == "JobExperimentationTime":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobExperimentationTime.JobExperimentationTime(name=name, description=feature_args["description"], job_num=count_index, job_map=self._game_schema["job_map"])
        elif feature_type == "JobGuideCount":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobGuideCount.JobGuideCount(name=name, description=feature_args["description"], job_num=count_index, job_map=self._game_schema["job_map"])
        elif feature_type == "JobHelpCount":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobHelpCount.JobHelpCount(name=name, description=feature_args["description"], job_num=count_index, job_map=self._game_schema["job_map"])
        elif feature_type == "JobModelingTime":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobModelingTime.JobModelingTime(name=name, description=feature_args["description"], job_num=count_index, job_map=self._game_schema["job_map"])
        elif feature_type == "JobStarted":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobStartCount.JobStarted(name=name, description=feature_args["description"], job_num=count_index, job_map=self._game_schema["job_map"])
        elif feature_type == "JobTasksCompleted":
            if count_index is None:
                raise TypeError("Got None for count_index, should have a value!")
            ret_val = JobTasksCompleted.JobTasksCompleted(name=name, description=feature_args["description"], job_num=count_index, job_map=self._game_schema["job_map"])
        elif feature_type == "SessionDiveSitesCount":
            ret_val = SessionDiveSitesCount.SessionDiveSitesCount(name=name, description=feature_args["description"])
        elif feature_type == "SessionDuration":
            ret_val = SessionDuration.SessionDuration(name=name, description=feature_args["description"])
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
        elif feature_type == "TotalArgumentationTime":
            ret_val = TotalArgumentationTime.TotalArgumentationTime(name=name, description=feature_args["description"])
        elif feature_type == "TotalDiveTime":
            ret_val = TotalDiveTime.TotalDiveTime(name=name, description=feature_args["description"])
        elif feature_type == "TotalExperimentationTime":
            ret_val = TotalExperimentationTime.TotalExperimentationTime(name=name, description=feature_args["description"])
        else:
            raise NotImplementedError(f"'{feature_type}' is not a valid feature for Aqualab.")
        return ret_val

    def getJobMap(self) -> Dict:
        return self._game_schema["job_map"]
