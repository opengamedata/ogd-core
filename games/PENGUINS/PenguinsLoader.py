## import standard libraries
import json
from typing import Any, Callable, Dict, List, Optional
## import local files
import games.PENGUINS.features
from extractors.detectors.Detector import Detector
from extractors.Extractor import ExtractorParameters
from extractors.ExtractorLoader import ExtractorLoader
from extractors.features.Feature import Feature
from games.PENGUINS.features import *
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.games.GameSchema import GameSchema
# from games.PENGUINS.DBExport import scene_map

## @class WaveExtractor
#  Extractor subclass for extracting features from Waves game data.

EXPORT_PATH = "games/PENGUINS/DBExport.json"

class PenguinsLoader(ExtractorLoader):

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @staticmethod
    def _getFeaturesModule():
        return games.PENGUINS.features
    
    def _loadFeature(self, feature_type:str, extractor_params:ExtractorParameters, schema_args:Dict[str,Any]) -> Feature:
        ret_val : Feature
        # Per-count features
            # level attempt features
        if feature_type == "SessionDuration":
            ret_val = SessionDuration.SessionDuration(params=extractor_params, session_id=self._session_id)
        elif feature_type == "RegionsEncountered":
            ret_val = RegionsEncountered.RegionsEncountered(params=extractor_params,region_map = self._region_map)
        elif feature_type == "PlayerWaddleCount":
            ret_val = PlayerWaddleCount.PlayerWaddleCount(params=extractor_params)
        elif feature_type == "GazeDuration":
            ret_val = GazeDuration.GazeDuration(params=extractor_params)
        elif feature_type == "GazeCount":
            ret_val = GazeCount.GazeCount(params=extractor_params)
        elif feature_type == "SnowBallDuration":
            ret_val = SnowBallDuration.SnowBallDuration(params=extractor_params)
        elif feature_type == "RingChimesCount":
            ret_val = RingChimesCount.RingChimesCount(params=extractor_params)
        elif feature_type == "RegionWaddleCount":
            ret_val = RegionWaddleCount.RegionWaddleCount(params=extractor_params)
        elif feature_type == "EatFishCount":
            ret_val = EatFishCount.EatFishCount(params=extractor_params)
        elif feature_type == "PickupRockCount":
            ret_val = PickupRockCount.PickupRockCount(params=extractor_params)
        elif feature_type == "EggLostCount":
            ret_val = EggLostCount.EggLostCount(params=extractor_params)
        elif feature_type == "EggRecoverTime":
            ret_val = EggRecoverTime.EggRecoverTime(params=extractor_params)
        # elif feature_type == "PlayerInactiveAvgDuration":
        #     ret_val = PlayerInactiveAvgDuration.PlayerInactiveAvgDuration(params=extractor_params)
        elif feature_type == "MirrorWaddleDuration":
            ret_val = MirrorWaddleDuration.MirrorWaddleDuration(params=extractor_params)
        
        elif extractor_params._count_index is not None:
            if feature_type == "RegionEnterCount":
                ret_val = RegionEnterCount.RegionEnterCount(params=extractor_params)
            elif feature_type == "WaddlePerRegion":
                    ret_val = WaddlePerRegion.WaddlePerRegion(params=extractor_params)
            elif feature_type == "RegionDuration":
                    ret_val = RegionDuration.RegionDuration(params=extractor_params)
            
        else:
            raise NotImplementedError(f"'{feature_type}' is not a valid feature for Penguins.")
        return ret_val

    def _loadDetector(self, detector_type:str, name:str, detector_args:Dict[str,Any], trigger_callback:Callable[[Event], None], count_index:Optional[int] = None) -> Detector:
        raise NotImplementedError(f"'{detector_type}' is not a valid detector for Waves.")

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
        self._region_map = {"no-active-region": 0}
        self._minX_map = {0: {"minX": 0} }
        self._minY_map = {0: {"minY": 0} }
        self._minZ_map = {0: {"minZ": 0} }
        self._maxX_map = {0: {"maxX": 0} }
        self._maxY_map = {0: {"maxY": 0} }
        self._maxZ_map = {0: {"maxZ": 0} }
        # Load Penguins jobs export and map job names to integer values
        with open(EXPORT_PATH, "r") as file:
            export = json.load(file)


            for i, regions in enumerate(export["regions"], start=1):
                self._region_map[regions["name"]] = i
                self._minX_map[i]=regions["minX"]
                self._minY_map[i]=regions["minY"]
                self._minZ_map[i]=regions["minZ"]
                self._maxX_map[i]=regions["maxX"]
                self._maxY_map[i]=regions["maxY"]
                self._maxZ_map[i]=regions["maxZ"]
                #self._min_bound[i] =list( regions["minX"],regions["minY"],regions["minZ"])
	            #self._max_bound[i] =list( regions["maxX"],regions["maxY"],regions["maxZ"])
            
        # Update level count
        self._game_schema._max_level = len(self._region_map) - 1

 