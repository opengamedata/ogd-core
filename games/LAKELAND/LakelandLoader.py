## import standard libraries
import sys
import logging
from datetime import datetime
from typing import Any, Dict, IO, List, Union
## import local files
import utils
from extractors.FeatureLoader import FeatureLoader
from features.Feature import Feature
from games.LAKELAND.extractors.LakelandExtractor import LakelandExtractor
from schemas.GameSchema import GameSchema

class LakelandLoader(FeatureLoader):
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
    def __init__(self, player_id:str, session_id:str, game_schema: GameSchema, output_file:Union[IO[str], None], feature_overrides:Union[List[str],None]):
        super().__init__(player_id=player_id, session_id=session_id, game_schema=game_schema, feature_overrides=feature_overrides)
        if output_file is not None:
            self._out_file = output_file
        else:
            utils.Logger.toStdOut(f"No output file given for Lakeland Extractor, defaulting to sys.stdout.", logging.WARN)
            self._out_file = sys.stdout

    def LoadFeature(self, feature_type:str, name:str, feature_args:Dict[str,Any], count_index:Union[int,None] = None) -> Feature:
        return LakelandExtractor(game_schema=self._game_schema, session_id=self._session_id, output_file=self._out_file)