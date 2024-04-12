## import standard libraries
from typing import Any, Callable, Dict, List, Optional
## import local files
from . import features
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.generators.extractors.Feature import Feature
from ogd.games.SHIPWRECKS.features import *
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.games.GameSchema import GameSchema

## @class ShipwrecksLoader
#  Extractor subclass for extracting features from Shipwrecks game data.
class ShipwrecksLoader(GeneratorLoader):
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
        return features

    def _loadFeature(self, feature_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any]) -> Feature:
        ret_val : Feature
        if extractor_params._count_index is None:
            match feature_type:
                case "ActiveJobs":
                    ret_val = ActiveJobs.ActiveJobs(params=extractor_params)
                case "EventList":
                    ret_val = EventList.EventList(params=extractor_params)
                case "EvidenceBoardCompleteCount":
                    ret_val = EvidenceBoardCompleteCount.EvidenceBoardCompleteCount(params=extractor_params)
                case "JobsCompleted":
                    ret_val = JobsCompleted.JobsCompleted(params=extractor_params, session_id=self._session_id)
                case "PlayerSummary":
                    ret_val = PlayerSummary.PlayerSummary(params=extractor_params)
                case "PopulationSummary":
                    ret_val = PopulationSummary.PopulationSummary(params=extractor_params)
                case "SessionDuration":
                    ret_val = SessionDuration.SessionDuration(params=extractor_params, session_id=self._session_id)
                case "SessionID":
                    ret_val = SessionID.SessionID(params=extractor_params, session_id=self._session_id)
                case "TopJobCompletionDestinations":
                    ret_val = TopJobCompletionDestinations.TopJobCompletionDestinations(params=extractor_params)
                case "TopJobSwitchDestinations":
                    ret_val = TopJobSwitchDestinations.TopJobSwitchDestinations(params=extractor_params)
                case "TotalDiveTime":
                    ret_val = TotalDiveTime.TotalDiveTime(params=extractor_params)
                case _:
                    raise NotImplementedError(f"'{feature_type}' is not a valid aggregate feature for Shipwrecks.")
        else:
            match feature_type:
                case "MissionDiveTime":
                    ret_val = MissionDiveTime.MissionDiveTime(params=extractor_params)
                case "JobsAttempted":
                    ret_val = JobsAttempted.JobsAttempted(params=extractor_params, mission_map=self._game_schema.NonStandardElements["mission_map"])
                case "MissionSonarTimeToComplete":
                    ret_val = MissionSonarTimeToComplete.MissionSonarTimeToComplete(params=extractor_params)
                case _:
                    raise NotImplementedError(f"'{feature_type}' is not a valid per-count feature for Shipwrecks.")
        return ret_val

    def _loadDetector(self, detector_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any], trigger_callback:Callable[[Event], None]) -> Detector:
        raise NotImplementedError(f"'{detector_type}' is not a valid feature for Shipwrecks.")
