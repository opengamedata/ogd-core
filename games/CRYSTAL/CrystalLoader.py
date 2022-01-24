## import standard libraries
import logging
from pydoc import describe
import typing
import traceback
from datetime import datetime
from typing import Any, Dict, List, Union
## import local files
from extractors.FeatureLoader import FeatureLoader
from extractors.Feature import Feature
from games.CRYSTAL.CrystalExtractor import CrystalExtractor
from schemas.GameSchema import GameSchema

class CrystalLoader(FeatureLoader):
    ## Constructor for the WaveExtractor class.
    #  Initializes some custom private data (not present in base class) for use
    #  when calculating some features.
    #  Sets the sessionID feature.
    #  Further, initializes all Q&A features to -1, representing unanswered questions.
    #
    #  @param session_id The id number for the session whose data is being processed
    #                    by this extractor instance.
    #  @param game_table A data structure containing information on how the db
    #                    table assiciated with this game is structured. 
    #  @param game_schema A dictionary that defines how the game data itself is
    #                     structured.
    def __init__(self, player_id:str, session_id:str, game_schema: GameSchema):
        super().__init__(player_id=player_id, session_id=session_id, game_schema=game_schema)

    def LoadFeature(self, feature_type:str, name:str, feature_args:Dict[str,Any], count_index:Union[int,None] = None) -> Feature:
        return CrystalExtractor(game_schema=self._game_schema, session_id=self._session_id)