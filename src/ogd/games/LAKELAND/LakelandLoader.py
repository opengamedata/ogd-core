## import standard libraries
from typing import Any, Callable, Dict, List, Optional
## import local files
from . import features
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.games.LAKELAND.features.LakelandExtractor import LakelandExtractor
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.configs.generators.GeneratorCollectionConfig import GeneratorCollectionConfig
from ogd.common.utils.Logger import Logger
from ogd.games.LAKELAND.features import *



class LakelandLoader(GeneratorLoader):

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _loadFeature(self, feature_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any]) -> Optional[Extractor]:
        ret_val: Optional[Extractor] = None

        # First run through aggregate features
        match feature_type:
            case "PersistenceTime":
                # ret_val = PersistenceTime.PersistenceTime(params=extractor_params)
                pass
            case "HouseBuildCount":
                ret_val = HouseBuildCount.HouseBuildCount(params=extractor_params)
            case "DairyBuildCount":
                ret_val = DairyBuildCount.DairyBuildCount(params=extractor_params)
            case "CropBuildCount":
                ret_val = CropBuildCount.CropBuildCount(params=extractor_params)
            case "TotalBuildCount":
                ret_val = TotalBuildCount.TotalBuildCount(params=extractor_params)
            case "HoversBeforeCropPlacement":
                ret_val = HoversBeforeCropPlacement.HoversBeforeCropPlacement(params=extractor_params)
            case "TotalEventsPerSession":
                ret_val = TotalEventsPerSession.TotalEventsPerSession(params=extractor_params)
            case "TotalSessionTime":
                threshold = schema_args.get("threshold", 50)
                ret_val = TotalSessionTime.TotalSessionTime(params=extractor_params, threshold=threshold)
            case _:
                ret_val = None

        return ret_val

    def _loadDetector(self, detector_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any], trigger_callback:Callable[[Event], None]) -> Optional[Detector]:
        Logger.Log(f"'{detector_type}' is not a valid feature for Lakeland.")
        return None

    @staticmethod
    def _getFeaturesModule():
        return features

    # *** BUILT-INS & PROPERTIES ***

    ## Constructor for the WaveExtractor class.
    def __init__(self, player_id:str, session_id:str, game_schema: GeneratorCollectionConfig, mode:ExtractionMode, feature_overrides:Optional[List[str]]):
        """Constructor for the CrystalLoader class.

        :param player_id: _description_
        :type player_id: str
        :param session_id: The id number for the session whose data is being processed by this instance
        :type session_id: str
        :param game_schema: A data structure containing information on how the game events and other data are structured
        :type game_schema: GeneratorCollectionConfig
        :param feature_overrides: A list of features to export, overriding the default of exporting all enabled features.
        :type feature_overrides: Optional[List[str]]
        """
        super().__init__(player_id=player_id, session_id=session_id, game_schema=game_schema, mode=mode, feature_overrides=feature_overrides)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
