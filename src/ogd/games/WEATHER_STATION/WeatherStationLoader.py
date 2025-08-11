## import standard libraries
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
## import local files
from . import features
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.generators.extractors.Feature import Feature
from ogd.games import WEATHER_STATION
from ogd.games.WEATHER_STATION.detectors import *
from ogd.games.WEATHER_STATION.features import *
# from ogd.games.PENGUINS.DBExport import scene_map
from ogd.core.generators.Generator import GeneratorParameters
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.schemas.games.GameSchema import GameSchema
from ogd.common.utils.Logger import Logger

## @class WaveExtractor
#  Extractor subclass for extracting features from Waves game data.

# EXPORT_PATH : Final[str] = "games/PENGUINS/DBExport.json"

class WeatherStationLoader(GeneratorLoader):
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
        self._region_map : List[Dict[str, Any]] = []

        # Load Weather Station jobs export and map job names to integer values
        _dbexport_path = Path(WEATHER_STATION.__file__) if Path(WEATHER_STATION.__file__).is_dir() else Path(WEATHER_STATION.__file__).parent
        with open(_dbexport_path / "DBExport.json", "r") as file:
            export = json.load(file)
            self._region_map = export.get("regions", [])

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @staticmethod
    def _getFeaturesModule():
        return features
    
    def _loadFeature(self, feature_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any]) -> Optional[Feature]:
        ret_val : Optional[Feature] = None
        if extractor_params._count_index == None:
            match feature_type:
                case _:
                    Logger.Log(f"'{feature_type}' is not a valid aggregate feature for Weather Station.")
        # Per-count features
        # level attempt features
        else:
            match feature_type:
                case _:
                    Logger.Log(f"'{feature_type}' is not a valid per-count feature for Weather Station.")
        return ret_val

    def _loadDetector(self, detector_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any], trigger_callback:Callable[[Event], None]) -> Optional[Detector]:
        ret_val : Optional[Detector] = None

        match detector_type:
            case _:
                Logger.Log(f"'{detector_type}' is not a valid detector for Weather Station.")
        return ret_val
