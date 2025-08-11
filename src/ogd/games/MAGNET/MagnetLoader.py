## import standard libraries
from typing import Any, Callable, Dict, List, Optional
## import local files
from . import features
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.core.generators.legacy.LegacyLoader import LegacyLoader
from ogd.games.MAGNET.features.MagnetExtractor import MagnetExtractor
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.core.configs.generators.GeneratorCollectionConfig import GeneratorCollectionConfig
from ogd.common.utils.Logger import Logger

class MagnetLoader(LegacyLoader):

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _loadExtractor(self, feature_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any]) -> Optional[Extractor]:
        return MagnetExtractor(params=extractor_params, generator_config=self._generator_config, session_id=self._session_id)

    def _loadDetector(self, detector_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any], trigger_callback:Callable[[Event], None]) -> Optional[Detector]:
        Logger.Log(f"'{detector_type}' is not a valid feature for Lakeland.")
        return None

    @staticmethod
    def _getFeaturesModule():
        return features

    # *** BUILT-INS & PROPERTIES ***

    ## Constructor for the WaveExtractor class.
    def __init__(self, player_id:str, session_id:str, generator_config:GeneratorCollectionConfig, mode:ExtractionMode, feature_overrides:Optional[List[str]]):
        """Constructor for the CrystalLoader class.

        :param player_id: _description_
        :type player_id: str
        :param session_id: The id number for the session whose data is being processed by this instance
        :type session_id: str
        :param generator_config: A data structure containing information on how the game events and other data are structured
        :type generator_config: GeneratorCollectionConfig
        :param feature_overrides: A list of features to export, overriding the default of exporting all enabled features.
        :type feature_overrides: Optional[List[str]]
        """
        super().__init__(player_id=player_id, session_id=session_id, generator_config=generator_config, mode=mode, feature_overrides=feature_overrides)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
