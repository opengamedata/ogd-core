## import standard libraries
import json
from pathlib import Path
from typing import Any, Callable, Dict, Final, List, Optional
## import local files
from . import features
from ogd.games import PENGUINS
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.generators.extractors.Feature import Feature
from ogd.games.PENGUINS.detectors import *
from ogd.games.PENGUINS.features import *
# from ogd.games.PENGUINS.DBExport import scene_map
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.schemas.games.GameSchema import GameSchema
from ogd.core.utils.Logger import Logger

## @class WaveExtractor
#  Extractor subclass for extracting features from Waves game data.

EXPORT_PATH : Final[str] = "games/PENGUINS/DBExport.json"

class PenguinsLoader(GeneratorLoader):
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

        # Load Penguins jobs export and map job names to integer values
        _dbexport_path = Path(PENGUINS.__file__) if Path(PENGUINS.__file__).is_dir() else Path(PENGUINS.__file__).parent
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
                case "ActivityCompleted":
                    ret_val = ActivityCompleted.ActivityCompleted(params=extractor_params)
                case "ActivityDuration":
                    ret_val = ActivityDuration.ActivityDuration(params=extractor_params)       
                case "BuiltNestCount":
                    ret_val = BuiltNestCount.BuiltNestCount(params=extractor_params)
                case "BuiltWrongNestCount":
                    ret_val = BuiltWrongNestCount.BuiltWrongNestCount(params=extractor_params)
                case "EatFishCount":
                    ret_val = EatFishCount.EatFishCount(params=extractor_params)
                case "EggLostCount":
                    ret_val = EggLostCount.EggLostCount(params=extractor_params)
                case "EggRecoverTime":
                    ret_val = EggRecoverTime.EggRecoverTime(params=extractor_params)
                case "GazeCount":
                    ret_val = GazeCount.GazeCount(params=extractor_params)
                case "GazeDuration":
                    ret_val = GazeDuration.GazeDuration(params=extractor_params)
                case "LogVersion":
                    ret_val = LogVersion.LogVersion(params=extractor_params)
                case "MirrorWaddleDuration":
                    ret_val = MirrorWaddleDuration.MirrorWaddleDuration(params=extractor_params)
                case "PenguinInteractCount":
                    ret_val = PenguinInteractCount.PenguinInteractCount(params=extractor_params)
                # case "PlayerInactiveAvgDuration":
                #     ret_val = PlayerInactiveAvgDuration.PlayerInactiveAvgDuration(params=extractor_params)
                case "RegionsEncountered":
                    ret_val = RegionsEncountered.RegionsEncountered(params=extractor_params)
                case "RingChimesCount":
                    ret_val = RingChimesCount.RingChimesCount(params=extractor_params)
                case "RockBashCount":
                    ret_val = RockBashCount.RockBashCount(params=extractor_params) 
                case "RockPickupCount":
                    ret_val = RockPickupCount.RockPickupCount(params=extractor_params)
                case "RockMultiplePickupCount":
                        ret_val = RockMultiplePickupCount.RockMultiplePickupCount(params=extractor_params)      
                case "SessionDuration":
                    ret_val = SessionDuration.SessionDuration(params=extractor_params, session_id=self._session_id)
                case "SkuaBashCount":
                        ret_val = SkuaBashCount.SkuaBashCount(params=extractor_params)
                case "SkuaPeckCount":
                        ret_val = SkuaPeckCount.SkuaPeckCount(params=extractor_params)
                case "SnowBallDuration":
                    ret_val = SnowBallDuration.SnowBallDuration(params=extractor_params)
                case "WaddleCount":
                    ret_val = WaddleCount.WaddleCount(params=extractor_params)
                case _:
                    Logger.Log(f"'{feature_type}' is not a valid aggregate feature for Penguins.")
        # Per-count features
        # level attempt features
        else:
            match feature_type:
                case "RegionDuration":
                            ret_val = RegionDuration.RegionDuration(params=extractor_params, region_map=self._region_map)
                case "RegionEnterCount":
                        ret_val = RegionEnterCount.RegionEnterCount(params=extractor_params, region_map=self._region_map)
                case "WaddlePerRegion":
                    ret_val = WaddlePerRegion.WaddlePerRegion(params=extractor_params, region_map=self._region_map)
                case _:
                    Logger.Log(f"'{feature_type}' is not a valid per-count feature for Penguins.")
        return ret_val

    def _loadDetector(self, detector_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any], trigger_callback:Callable[[Event], None]) -> Optional[Detector]:
        ret_val : Optional[Detector] = None

        match detector_type:
            case "RegionEnter":
                ret_val = RegionEnter.RegionEnter(params=extractor_params, trigger_callback=trigger_callback, region_map=self._region_map)
            case "RegionExit":
                ret_val = RegionExit.RegionExit(params=extractor_params, trigger_callback=trigger_callback, region_map=self._region_map)
            case _:
                Logger.Log(f"'{detector_type}' is not a valid detector for Penguins.")
        return ret_val
