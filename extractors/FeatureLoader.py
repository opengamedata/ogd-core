# global imports
import abc
from typing import Any, Dict, Union
# local imports
from extractors.Feature import Feature
from schemas.GameSchema import GameSchema

class FeatureLoader(abc.ABC):
    # *** ABSTRACTS ***
    
    @abc.abstractmethod
    def LoadFeature(self, feature_type:str, name:str, feature_args:Dict[str,Any], count_index:Union[int,None] = None) -> Feature:
        pass

    def __init__(self, player_id:str, session_id:str, game_schema:GameSchema):
        """Base constructor for Extractor classes.
        The constructor sets an extractor's session id and range of levels,
        as well as initializing the feature
        es dictionary and list of played levels.

        :param session_id: The id of the session from which we will extract features.
        :type session_id: str
        :param game_schema: A dictionary that defines how the game data itself is structured.
        :type game_schema: GameSchema
        """
        self._player_id   : str        = player_id
        self._session_id  : str        = session_id
        self._game_schema : GameSchema = game_schema
