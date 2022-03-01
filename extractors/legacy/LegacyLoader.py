# global imports
from typing import List, Union
# local imports
from extractors.FeatureLoader import FeatureLoader
from extractors.FeatureRegistry import FeatureRegistry
from schemas.GameSchema import GameSchema

class LegacyLoader(FeatureLoader):
    def __init__(self, player_id:str, session_id:str, feature_overrides:Union[List[str],None]):
        super().__init__(player_id=player_id, session_id=session_id, feature_overrides=feature_overrides)

    def LoadToRegistry(self, registry:FeatureRegistry, game_schema:GameSchema) -> None:
        feat = self.LoadFeature(feature_type="", name="", feature_args={}, count_index=0)
        # treat the monolithic LegacyFeature extractor as a single aggregate.
        registry.Register(feat, FeatureRegistry.Listener.Kinds.AGGREGATE)