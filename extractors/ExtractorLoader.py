# import libraries
import abc
import logging
from typing import Any, Callable, Dict, List, Optional
from extractors.detectors.Detector import Detector
from extractors.Extractor import ExtractorParameters
# import locals
from extractors.detectors.DetectorRegistry import DetectorRegistry
from extractors.ExtractorRegistry import ExtractorRegistry
from extractors.features.Feature import Feature
from extractors.features.FeatureRegistry import FeatureRegistry
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.IterationMode import IterationMode
from schemas.GameSchema import GameSchema
from utils import Logger

class ExtractorLoader(abc.ABC):

    # *** ABSTRACTS ***
    
    @abc.abstractmethod
    def _loadFeature(self, feature_type:str, extractor_params:ExtractorParameters, schema_args:Dict[str,Any]) -> Feature:
        pass
    
    @abc.abstractmethod
    def _loadDetector(self, detector_type:str, extractor_params:ExtractorParameters, schema_args:Dict[str,Any], trigger_callback:Callable[[Event], None]) -> Detector:
        pass

    # *** BUILT-INS ***

    def __init__(self, player_id:str, session_id:str, game_schema:GameSchema, mode:ExtractionMode, feature_overrides:Optional[List[str]]):
        """Base constructor for Extractor classes.
        The constructor sets an extractor's session id and range of levels,
        as well as initializing the feature
        es dictionary and list of played levels.

        :param session_id: The id of the session from which we will extract features.
        :type session_id: str
        :param game_schema: A dictionary that defines how the game data itself is structured.
        :type game_schema: GameSchema
        """
        self._player_id   : str            = player_id
        self._session_id  : str            = session_id
        self._game_schema : GameSchema     = game_schema
        self._mode        : ExtractionMode = mode
        self._overrides   : Optional[List[str]] = feature_overrides

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def LoadFeature(self, feature_type:str, name:str, schema_args:Dict[str,Any], count_index:Optional[int] = None) -> Feature:
        params = ExtractorParameters(name=name, description=schema_args.get('description',""), mode=self._mode, count_index=count_index)
        return self._loadFeature(feature_type=feature_type, extractor_params=params, schema_args=schema_args)
    
    def LoadDetector(self, detector_type:str, name:str, schema_args:Dict[str,Any], trigger_callback:Callable[[Event], None], count_index:Optional[int] = None) -> Detector:
        params = ExtractorParameters(name=name, description=schema_args.get('description',""), mode=self._mode, count_index=count_index)
        return self._loadDetector(detector_type=detector_type, extractor_params=params, schema_args=schema_args, trigger_callback=trigger_callback)

    def LoadToFeatureRegistry(self, schema:GameSchema, registry:FeatureRegistry) -> None:
        # first, load aggregate features
        for name,aggregate in schema.AggregateFeatures.items():
            if self._validateFeature(name=name, iter_mode=IterationMode.AGGREGATE, overrides=self._overrides):
                try:
                    feature = self.LoadFeature(feature_type=name, name=name, schema_args=aggregate)
                except NotImplementedError as err:
                    Logger.Log(f"In ExtractorLoader, '{name}' is not a valid feature for {schema._game_name}", logging.ERROR)
                else:
                    registry.Register(feature, ExtractorRegistry.Listener.Kinds.AGGREGATE)
        for name,percount in schema.PerCountFeatures.items():
            if self._validateFeature(name=name, iter_mode=IterationMode.PERCOUNT, overrides=self._overrides):
                for i in ExtractorLoader._genCountRange(count=percount["count"], schema=schema):
                    try:
                        feat_name = f"{percount['prefix']}{i}_{name}"
                        feature = self.LoadFeature(feature_type=name, name=feat_name, schema_args=percount, count_index=i)
                    except NotImplementedError as err:
                        Logger.Log(f"In ExtractorLoader, '{name}' is not a valid feature for {schema._game_name}", logging.ERROR)
                    else:
                        registry.Register(extractor=feature, kind=ExtractorRegistry.Listener.Kinds.PERCOUNT)

    def LoadToDetectorRegistry(self, schema:GameSchema, registry:DetectorRegistry, trigger_callback:Callable[[Event], None]) -> None:
        # first, load aggregate features
        for name,aggregate in schema.AggregateDetectors.items():
            if self._validateFeature(name=name, iter_mode=IterationMode.AGGREGATE, overrides=self._overrides):
                try:
                    detector = self.LoadDetector(detector_type=name, name=name, schema_args=aggregate, trigger_callback=trigger_callback)
                except NotImplementedError as err:
                    Logger.Log(f"In ExtractorLoader, '{name}' is not a valid detector for {schema._game_name}", logging.ERROR)
                else:
                    registry.Register(detector, ExtractorRegistry.Listener.Kinds.AGGREGATE)
        for name,percount in schema.PerCountDetectors.items():
            if self._validateFeature(name=name, iter_mode=IterationMode.PERCOUNT, overrides=self._overrides):
                for i in ExtractorLoader._genCountRange(count=percount["count"], schema=schema):
                    try:
                        detector = self.LoadDetector(detector_type=name, name=f"{percount['prefix']}{i}_{name}", schema_args=percount, trigger_callback=trigger_callback, count_index=i)
                    except NotImplementedError as err:
                        Logger.Log(f"In ExtractorLoader, '{name}' is not a valid detector for {schema._game_name}", logging.ERROR)
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

    # *** PRIVATE METHODS ***

    def _validateFeature(self, name:str, iter_mode:IterationMode, overrides:Optional[List[str]]):
        _is_enabled = self._game_schema.FeatureEnabled(feature_name=name, iter_mode=iter_mode, extract_mode=self._mode)
        if overrides is not None:
            if name in overrides:
                return _is_enabled
            else:
                return False
        else:
            return _is_enabled
