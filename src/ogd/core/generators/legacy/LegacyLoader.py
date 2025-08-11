# import libraries
from typing import List, Optional, Type
# import locals
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.configs.GameStoreConfig import GameStoreConfig

class LegacyLoader(GeneratorLoader):
    def __init__(self, player_id:str, session_id:str, game_schema:GameStoreConfig, mode:ExtractionMode, feature_overrides:Optional[List[str]]):
        super().__init__(player_id=player_id, session_id=session_id, generator_config=game_schema, mode=mode, feature_overrides=feature_overrides)

    def GetFeatureClass(self, feature_type:str) -> Optional[Type[Extractor]]:
        return None

    def _validateMode(self, feature_type) -> bool:
        """Overridden version of _validateMode.
        For LegacyLoader, we never care to check modes, since feature is a monolith and should just go for all versions.

        :param feature_type: _description_
        :type feature_type: _type_
        :return: _description_
        :rtype: bool
        """
        return True
