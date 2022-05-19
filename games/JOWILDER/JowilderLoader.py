## import standard libraries
from typing import Any, Callable, Dict, List, Optional
## import local files
from detectors.Detector import Detector
from features.Feature import Feature
from processors.legacy.LegacyLoader import LegacyLoader
from games.JOWILDER.features.JowilderExtractor import JowilderExtractor
from schemas.Event import Event
from schemas.GameSchema import GameSchema

class JowilderLoader(LegacyLoader):

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _loadFeature(self, feature_type:str, name:str, feature_args:Dict[str,Any], count_index:Optional[int] = None) -> Feature:
        return JowilderExtractor(game_schema=self._game_schema, session_id=self._session_id)

    def _loadDetector(self, detector_type:str, name:str, detector_args:Dict[str,Any], trigger_callback:Callable[[Event], None], count_index:Optional[int] = None) -> Detector:
        raise NotImplementedError(f"'{detector_type}' is not a valid feature for Lakeland.")

    # *** BUILT-INS ***

    ## Constructor for the WaveExtractor class.
    def __init__(self, player_id:str, session_id:str, game_schema: GameSchema, feature_overrides:Optional[List[str]]):
        """Constructor for the CrystalLoader class.

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