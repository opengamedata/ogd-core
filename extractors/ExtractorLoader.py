# import libraries
import abc
import logging
from typing import Any, Callable, Dict, List, Optional
from detectors.Detector import Detector
# import locals
from detectors.DetectorRegistry import DetectorRegistry
from extractors.ExtractorRegistry import ExtractorRegistry
from features.Feature import Feature
from features.FeatureRegistry import FeatureRegistry
from schemas.Event import Event
from schemas.GameSchema import GameSchema
from utils import Logger

class ExtractorLoader(abc.ABC):

    # *** ABSTRACTS ***
    
    @abc.abstractmethod
    def _loadFeature(self, feature_type:str, name:str, feature_args:Dict[str,Any], count_index:Optional[int] = None) -> Feature:
        pass
    
    @abc.abstractmethod
    def _loadDetector(self, detector_type:str, name:str, detector_args:Dict[str,Any], trigger_callback:Callable[[Event], None], count_index:Optional[int] = None) -> Detector:
        pass

    # *** BUILT-INS ***

    def __init__(self, player_id:str, session_id:str, game_schema:GameSchema, feature_overrides:Optional[List[str]]):
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
        self._overrides   : Optional[List[str]]    = feature_overrides

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def LoadFeature(self, feature_type:str, name:str, feature_args:Dict[str,Any], count_index:Optional[int] = None) -> Feature:
        return self._loadFeature(feature_type=feature_type, name=name, feature_args=feature_args, count_index=count_index)
    
    def LoadDetector(self, detector_type:str, name:str, detector_args:Dict[str,Any], trigger_callback:Callable[[Event], None], count_index:Optional[int] = None) -> Detector:
        return self._loadDetector(detector_type=detector_type, name=name, detector_args=detector_args, trigger_callback=trigger_callback, count_index=count_index)

    def LoadToFeatureRegistry(self, registry:FeatureRegistry) -> None:
        # first, load aggregate features
        for name,aggregate in self._game_schema.aggregate_features().items():
            if ExtractorLoader._validateFeature(name=name, base_setting=aggregate.get('enabled', False), overrides=self._overrides):
                try:
                    feature = self.LoadFeature(feature_type=name, name=name, feature_args=aggregate)
                except NotImplementedError as err:
                    Logger.Log(f"In ExtractorLoader, '{name}' is not a valid feature for {self._game_schema._game_name}", logging.ERROR)
                else:
                    registry.Register(feature, ExtractorRegistry.Listener.Kinds.AGGREGATE)
        for name,percount in self._game_schema.percount_features().items():
            if ExtractorLoader._validateFeature(name=name, base_setting=percount.get('enabled', False), overrides=self._overrides):
                for i in ExtractorLoader._genCountRange(count=percount["count"], schema=self._game_schema):
                    try:
                        feat_name = f"{percount['prefix']}{i}_{name}"
                        feature = self.LoadFeature(feature_type=name, name=feat_name, feature_args=percount, count_index=i)
                    except NotImplementedError as err:
                        Logger.Log(f"In ExtractorLoader, '{name}' is not a valid feature for {self._game_schema._game_name}", logging.ERROR)
                    else:
                        registry.Register(extractor=feature, kind=ExtractorRegistry.Listener.Kinds.PERCOUNT)

    def LoadToDetectorRegistry(self, registry:DetectorRegistry, trigger_callback:Callable[[Event], None]) -> None:
        # first, load aggregate features
        for name,aggregate in self._game_schema.aggregate_detectors().items():
            if ExtractorLoader._validateFeature(name=name, base_setting=aggregate.get('enabled', False), overrides=self._overrides):
                try:
                    detector = self.LoadDetector(detector_type=name, name=name, detector_args=aggregate, trigger_callback=trigger_callback)
                except NotImplementedError as err:
                    Logger.Log(f"In ExtractorLoader, '{name}' is not a valid detector for {self._game_schema._game_name}", logging.ERROR)
                else:
                    registry.Register(detector, ExtractorRegistry.Listener.Kinds.AGGREGATE)
        for name,percount in self._game_schema.percount_detectors().items():
            if ExtractorLoader._validateFeature(name=name, base_setting=percount.get('enabled', False), overrides=self._overrides):
                for i in ExtractorLoader._genCountRange(count=percount["count"], schema=self._game_schema):
                    try:
                        detector = self.LoadDetector(detector_type=name, name=f"{percount['prefix']}{i}_{name}", detector_args=percount, trigger_callback=trigger_callback, count_index=i)
                    except NotImplementedError as err:
                        Logger.Log(f"In ExtractorLoader, '{name}' is not a valid detector for {self._game_schema._game_name}", logging.ERROR)
                    else:
                        registry.Register(extractor=detector, kind=ExtractorRegistry.Listener.Kinds.PERCOUNT)

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _genCountRange(count:Any, schema:GameSchema) -> range:
        if type(count) == str and count.lower() == "level_range":
            count_range = schema.level_range()
        else:
            count_range = range(0,int(count))
        return count_range

    @staticmethod
    def _validateFeature(name:str, base_setting:bool, overrides:Optional[List[str]]):
        if overrides is not None:
            if name in overrides:
                return base_setting
            else:
                return False
        else:
            return base_setting

    # *** PRIVATE METHODS ***
