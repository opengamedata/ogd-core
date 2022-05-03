# import libraries
from typing import Callable, List, Union
# import locals
from detectors.DetectorRegistry import DetectorRegistry
from extractors.ExtractorRegistry import ExtractorRegistry
from extractors.ExtractorLoader import ExtractorLoader
from features.FeatureRegistry import FeatureRegistry
from processors.legacy.LegacyDetector import LegacyDetector
from schemas.Event import Event
from schemas.GameSchema import GameSchema

class LegacyLoader(ExtractorLoader):
    def __init__(self, player_id:str, session_id:str, game_schema:GameSchema, feature_overrides:Union[List[str],None]):
        super().__init__(player_id=player_id, session_id=session_id, game_schema=game_schema, feature_overrides=feature_overrides)

    def LoadToFeatureRegistry(self, registry:FeatureRegistry) -> None:
        feat = self.LoadFeature(feature_type="", name="", feature_args={}, count_index=0)
        # treat the monolithic LegacyFeature extractor as a single aggregate.
        registry.Register(feat, ExtractorRegistry.Listener.Kinds.AGGREGATE)

    def LoadToDetectorRegistry(self, registry:DetectorRegistry, trigger_callback:Callable[[Event], None]) -> None:
        feat = self.LoadDetector(detector_type="", name="", detector_args={}, trigger_callback=trigger_callback, count_index=0)
        registry.Register(feat, ExtractorRegistry.Listener.Kinds.AGGREGATE)