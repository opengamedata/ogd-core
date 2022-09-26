# import libraries
from typing import List, Optional
# import locals
from extractors.ExtractorLoader import ExtractorLoader
from schemas.ExtractionMode import ExtractionMode
from schemas.GameSchema import GameSchema

class LegacyLoader(ExtractorLoader):
    def __init__(self, player_id:str, session_id:str, game_schema:GameSchema, mode:ExtractionMode, feature_overrides:Optional[List[str]]):
        super().__init__(player_id=player_id, session_id=session_id, game_schema=game_schema, mode=mode, feature_overrides=feature_overrides)

    def _validateMode(self, feature_type) -> bool:
        """Overridden version of _validateMode.
        For LegacyLoader, we never care to check modes, since feature is a monolith and should just go for all versions.

        :param feature_type: _description_
        :type feature_type: _type_
        :return: _description_
        :rtype: bool
        """
        return True
