# import libraries
import logging
from typing import Any, Callable, Dict, List, Optional
# import locals
from extractors.registries.DetectorRegistry import DetectorRegistry
from extractors.Extractor import ExtractorParameters
from extractors.ExtractorLoader import ExtractorLoader
from extractors.registries.FeatureRegistry import FeatureRegistry
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.GameSchema import GameSchema
from schemas.IterationMode import IterationMode
from utils import Logger

class LegacyLoader(ExtractorLoader):
    def __init__(self, player_id:str, session_id:str, game_schema:GameSchema, mode:ExtractionMode, feature_overrides:Optional[List[str]]):
        super().__init__(player_id=player_id, session_id=session_id, game_schema=game_schema, mode=mode, feature_overrides=feature_overrides)

    # def LoadToFeatureRegistry(self, registry:FeatureRegistry) -> None:
    #     feat = self.LoadFeature(feature_type="", name="", schema_args={}, count_index=0)
    #     # treat the monolithic LegacyFeature extractor as a single aggregate.
    #     if feat is not None:
    #         registry.Register(feat, IterationMode.AGGREGATE)

    # def LoadToDetectorRegistry(self, registry:DetectorRegistry, trigger_callback:Callable[[Event], None]) -> None:
    #     try:
    #         feat = self.LoadDetector(detector_type="", name="", schema_args={}, trigger_callback=trigger_callback, count_index=0)
    #         if feat is not None:
    #             registry.Register(feat, IterationMode.AGGREGATE)
    #     except NotImplementedError as err:
    #         Logger.Log("No detectors to be loaded.", logging.INFO, depth=2)

    def _validateMode(self, feature_type) -> bool:
        """Overridden version of _validateMode.
        For LegacyLoader, we never care to check modes, since feature is a monolith and should just go for all versions.

        :param feature_type: _description_
        :type feature_type: _type_
        :return: _description_
        :rtype: bool
        """
        return True
