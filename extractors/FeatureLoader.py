# global imports
import abc
import logging
from typing import Any, Dict, List, Union
# local imports
import utils
from extractors.Feature import Feature
from extractors.FeatureRegistry import FeatureRegistry
from schemas.GameSchema import GameSchema

class FeatureLoader(abc.ABC):
    # *** ABSTRACTS ***
    
    @abc.abstractmethod
    def LoadFeature(self, feature_type:str, name:str, feature_args:Dict[str,Any], count_index:Union[int,None] = None) -> Feature:
        pass

    def __init__(self, player_id:str, session_id:str, game_schema:GameSchema, feature_overrides:Union[List[str],None]):
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
        self._overrides   : Union[List[str],None]    = feature_overrides

    def LoadToRegistry(self, registry:FeatureRegistry) -> None:
        # first, liad aggregate features
        for name,aggregate in self._game_schema.aggregate_features().items():
            if FeatureLoader._validateFeature(name=name, base_setting=aggregate.get('enabled', False), overrides=self._overrides):
                try:
                    feature = self.LoadFeature(feature_type=name, name=name, feature_args=aggregate)
                except NotImplementedError as err:
                    utils.Logger.Log(f"{name} is not a valid feature for {self._game_schema._game_name}", logging.ERROR)
                else:
                    registry.Register(feature, FeatureRegistry.Listener.Kinds.AGGREGATE)
        for name,percount in self._game_schema.percount_features().items():
            if FeatureLoader._validateFeature(name=name, base_setting=percount.get('enabled', False), overrides=self._overrides):
                for i in FeatureLoader._genCountRange(count=percount["count"], schema=self._game_schema):
                    try:
                        feature = self.LoadFeature(feature_type=name, name=f"{percount['prefix']}{i}_{name}", feature_args=percount, count_index=i)
                    except NotImplementedError as err:
                        utils.Logger.Log(f"{name} is not a valid feature for {self._game_schema._game_name}", logging.ERROR)
                    else:
                        registry.Register(feature=feature, kind=FeatureRegistry.Listener.Kinds.PERCOUNT)

    # *** PRIVATE STATICS ***

    @staticmethod
    def _genCountRange(count:Any, schema:GameSchema) -> range:
        if type(count) == str and count.lower() == "level_range":
            count_range = schema.level_range()
        else:
            count_range = range(0,int(count))
        return count_range

    @staticmethod
    def _validateFeature(name:str, base_setting:bool, overrides:Union[List[str],None]):
        if overrides is not None:
            if name in overrides:
                return base_setting
            else:
                return False
        else:
            return base_setting

