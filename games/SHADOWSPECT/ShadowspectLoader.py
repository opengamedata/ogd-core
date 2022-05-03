## import standard libraries
from typing import Any, Callable, Dict, List, Union
## import local files
from detectors.Detector import Detector
from games.SHADOWSPECT.features import *
from extractors.ExtractorLoader import ExtractorLoader
from features.Feature import Feature
from schemas.Event import Event
from schemas.GameSchema import GameSchema

## @class ShadowspectExtractor
#  Extractor subclass for extracting features from Shadowspects game data.
class ShadowspectLoader(ExtractorLoader):

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _loadFeature(self, feature_type:str, name:str, feature_args:Dict[str,Any], count_index:Union[int,None] = None) -> Feature:
        ret_val : Feature
        if feature_type == "MoveShapeCount":
            ret_val = MoveShapeCount.MoveShapeCount(name=name, description=feature_args["description"])
        elif feature_type == "SessionID":
            ret_val = SessionID.SessionID(name=name, description=feature_args["description"], session_id=self._session_id)
        elif feature_type == "FunnelByUser":
            ret_val = FunnelByUser.FunnelByUser(name=name, description=feature_args["description"])
        elif feature_type == "LevelsOfDifficulty":
            ret_val = LevelsOfDifficulty.LevelsOfDifficulty(name=name, description=feature_args["description"])
        elif feature_type == "SequenceBetweenPuzzles":
            ret_val = SequenceBetweenPuzzles.SequenceBetweenPuzzles(name=name, description=feature_args["description"])
        else:
            raise NotImplementedError(f"'{feature_type}' is not a valid feature for Shadowspect.")
        return ret_val

    def _loadDetector(self, detector_type: str, name: str, detector_args: Dict[str, Any], count_index: Union[int, None] = None) -> Detector:
        raise NotImplementedError(f"'{detector_type}' is not a valid feature for Shadowspect.")

    ## Constructor for the ShadowspectExtractor class.
    def __init__(self, player_id:str, session_id: str, game_schema: GameSchema, feature_overrides:Union[List[str],None]=None):
        """Constructor for the CrystalLoader class.

        :param player_id: _description_
        :type player_id: str
        :param session_id: The id number for the session whose data is being processed by this instance
        :type session_id: str
        :param game_schema: A data structure containing information on how the game events and other data are structured
        :type game_schema: GameSchema
        :param feature_overrides: A list of features to export, overriding the default of exporting all enabled features.
        :type feature_overrides: Union[List[str],None]
        """
        self._game_schema = game_schema
        super().__init__(player_id=player_id, session_id=session_id, game_schema=game_schema, feature_overrides=feature_overrides)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
