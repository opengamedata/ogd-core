## import standard libraries
from typing import Any, Callable, Dict, List, Optional
## import local files
from .extractors import builtin
from ogd.core.generators.extractors.builtin import *
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.games.GameSchema import GameSchema

## @class WaveExtractor
#  Extractor subclass for extracting features from Waves game data.
class BuiltinLoader(GeneratorLoader):

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @staticmethod
    def _getFeaturesModule():
        return builtin
    
    def _loadFeature(self, feature_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any]) -> Feature:
        ret_val : Feature
        # Session-level features.
        if extractor_params._count_index is None:
            match feature_type:
                case "CountEvent":
                    ret_val = CountEvent.CountEvent(params=extractor_params, schema_args=schema_args)
                case "Timespan":
                    ret_val = Timespan.Timespan(params=extractor_params, schema_args=schema_args)
                case _:
                    raise NotImplementedError(f"'{feature_type}' is not a valid built-in session feature.")
        # Per-count features
        # level attempt features
        else:
            match feature_type:
                case _:
                    raise NotImplementedError(f"'{feature_type}' is not a valid built-in per-count feature.")
        return ret_val

    def _loadDetector(self, detector_type:str, name:str, detector_args:Dict[str,Any], trigger_callback:Callable[[Event], None], count_index:Optional[int] = None) -> Detector:
        raise NotImplementedError(f"'{detector_type}' is not a valid built-in detector.")

    # *** BUILT-INS & PROPERTIES ***

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
