## import standard libraries
from typing import Any, Callable, Dict, List, Optional
## import local files
import games.SHIPWRECKS.features
from extractors.detectors.Detector import Detector
from extractors.Extractor import ExtractorParameters
from extractors.ExtractorLoader import ExtractorLoader
from extractors.features.Feature import Feature
from games.SHIPWRECKS.features import *
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.GameSchema import GameSchema

## @class ShipwrecksLoader
#  Extractor subclass for extracting features from Shipwrecks game data.
class ShipwrecksLoader(ExtractorLoader):
    ## Constructor for the ShipwrecksLoader class.
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
    def __init__(self, player_id:str, session_id:str, game_schema: GameSchema, mode:ExtractionMode, feature_overrides:Optional[List[str]]):
        super().__init__(player_id=player_id, session_id=session_id, game_schema=game_schema, mode=mode, feature_overrides=feature_overrides)

    @staticmethod
    def _getFeaturesModule():
        return games.SHIPWRECKS.features

    def _loadFeature(self, feature_type:str, extractor_params:ExtractorParameters, schema_args:Dict[str,Any]) -> Feature:
        ret_val : Feature
        if feature_type == "ActiveJobs":
            ret_val = ActiveJobs.ActiveJobs(params=extractor_params)
        elif feature_type == "MissionDiveTime":
            if extractor_params._count_index is None:
                raise TypeError("Got None for extractor_params._count_index, should have a value!")
            else:
                ret_val = MissionDiveTime.MissionDiveTime(params=extractor_params)
        elif feature_type == "JobsAttempted":
            if extractor_params._count_index is None:
                raise TypeError("Got None for extractor_params._count_index, should have a value!")
            ret_val = JobsAttempted.JobsAttempted(params=extractor_params, mission_map=self._game_schema.NonStandardElements["mission_map"])
        elif feature_type == "MissionSonarTimeToComplete":
            if extractor_params._count_index is None:
                raise TypeError("Got None for extractor_params._count_index, should have a value!")
            else:
                ret_val = MissionSonarTimeToComplete.MissionSonarTimeToComplete(params=extractor_params)
        elif feature_type == "EventList":
            ret_val = EventList.EventList(params=extractor_params)
        elif feature_type == "EvidenceBoardCompleteCount":
            ret_val = EvidenceBoardCompleteCount.EvidenceBoardCompleteCount(params=extractor_params)
        elif feature_type == "JobsCompleted":
            ret_val = JobsCompleted.JobsCompleted(params=extractor_params, session_id=self._session_id)
        elif feature_type == "PlayerSummary":
            ret_val = PlayerSummary.PlayerSummary(params=extractor_params)
        elif feature_type == "PopulationSummary":
            ret_val = PopulationSummary.PopulationSummary(params=extractor_params)
        elif feature_type == "SessionDuration":
            ret_val = SessionDuration.SessionDuration(params=extractor_params, session_id=self._session_id)
        elif feature_type == "SessionID":
            ret_val = SessionID.SessionID(params=extractor_params, session_id=self._session_id)
        elif feature_type == "TopJobCompletionDestinations":
            ret_val = TopJobCompletionDestinations.TopJobCompletionDestinations(params=extractor_params)
        elif feature_type == "TopJobSwitchDestinations":
            ret_val = TopJobSwitchDestinations.TopJobSwitchDestinations(params=extractor_params)
        elif feature_type == "TotalDiveTime":
            ret_val = TotalDiveTime.TotalDiveTime(params=extractor_params)
        else:
            raise NotImplementedError(f"'{feature_type}' is not a valid feature for Shipwrecks.")
        return ret_val

    def _loadDetector(self, detector_type:str, extractor_params:ExtractorParameters, schema_args:Dict[str,Any], trigger_callback:Callable[[Event], None]) -> Detector:
        raise NotImplementedError(f"'{detector_type}' is not a valid feature for Shipwrecks.")
