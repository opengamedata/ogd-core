## import standard libraries
from typing import Any, Callable, Dict, List, Optional
## import local files
import games.ICECUBE.features
from extractors.detectors.Detector import Detector
from extractors.Extractor import ExtractorParameters
from extractors.ExtractorLoader import ExtractorLoader
from extractors.features.Feature import Feature
from games.ICECUBE.features import *
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.GameSchema import GameSchema

## @class WaveExtractor
#  Extractor subclass for extracting features from Waves game data.
class IcecubeLoader(ExtractorLoader):

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @staticmethod
    def _getFeaturesModule():
        return games.ICECUBE.features
    
    def _loadFeature(self, feature_type:str, extractor_params:ExtractorParameters, schema_args:Dict[str,Any]) -> Feature:
        ret_val : Feature
        # Per-count features
            # level attempt features
        if feature_type == "ScenesEncountered":
            ret_val = ScenesEncountered.ScenesEncountered(params=extractor_params)
        else:
            raise NotImplementedError(f"'{feature_type}' is not a valid feature for Waves.")
        return ret_val

    def _loadDetector(self, detector_type:str, name:str, detector_args:Dict[str,Any], trigger_callback:Callable[[Event], None], count_index:Optional[int] = None) -> Detector:
        raise NotImplementedError(f"'{detector_type}' is not a valid detector for Waves.")

    # *** BUILT-INS ***

    ## Constructor for the WaveLoader class.
    def __init__(self, player_id:str, session_id: str, game_schema:GameSchema, mode:ExtractionMode, feature_overrides:Optional[List[str]]=None):
        """Constructor for the WaveLoader class.

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
