# import libraries
import abc
import logging
from typing import Any, Callable, Dict, List, Optional

from numpy import extract
from extractors.detectors.Detector import Detector
from extractors.Extractor import ExtractorParameters
# import locals
from extractors.detectors.DetectorRegistry import DetectorRegistry
from extractors.Extractor import Extractor
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
    
    def LoadDetector(self, detector_type:str, name:str, schema_args:Dict[str,Any], trigger_callback:Callable[[Event], None], count_index:Optional[int] = None) -> Optional[Detector]:
        ret_val = None

        params = ExtractorParameters(name=name, description=schema_args.get('description',""), mode=self._mode, count_index=count_index)
        try:
            ret_val = self._loadDetector(detector_type=detector_type, extractor_params=params, schema_args=schema_args, trigger_callback=trigger_callback)
        except NotImplementedError as err:
            Logger.Log(f"In ExtractorLoader, '{name}' is not a valid detector for {self._game_schema.GameName}", logging.ERROR)

        return ret_val

    def LoadFeature(self, feature_type:str, name:str, schema_args:Dict[str,Any], count_index:Optional[int] = None) -> Optional[Feature]:
        ret_val = None

        params = ExtractorParameters(name=name, description=schema_args.get('description',""), mode=self._mode, count_index=count_index)
        try:
            ret_val = self._loadFeature(feature_type=feature_type, extractor_params=params, schema_args=schema_args)
        except NotImplementedError as err:
            Logger.Log(f"In ExtractorLoader, '{name}' is not a valid feature for {self._game_schema._game_name}", logging.ERROR)

        return ret_val

    def RegisterExtractor(self, registry:ExtractorRegistry, extractor:Extractor, iter_mode:IterationMode):
        if self._mode in extract.AvailableModes():
            registry.Register(extractor=extractor, mode=iter_mode)

    def LoadToDetectorRegistry(self, registry:DetectorRegistry, trigger_callback:Callable[[Event], None]) -> None:
        # first, load aggregate features
        iter_mode = IterationMode.AGGREGATE
        for base_name,aggregate in self._game_schema.AggregateDetectors.items():
            if self._game_schema.DetectorEnabled(detector_name=base_name, iter_mode=iter_mode, extract_mode=self._mode, overrides=self._overrides):
                detector = self.LoadDetector(detector_type=base_name, name=base_name, schema_args=aggregate, trigger_callback=trigger_callback)
                if detector is not None:
                    self.RegisterExtractor(registry=registry, extractor=detector, iter_mode=iter_mode)
        iter_mode = IterationMode.PERCOUNT
        for base_name,percount in self._game_schema.PerCountDetectors.items():
            if self._game_schema.DetectorEnabled(detector_name=base_name, iter_mode=iter_mode, extract_mode=self._mode, overrides=self._overrides):
                for i in ExtractorLoader._genCountRange(count=percount["count"], schema=self._game_schema):
                    instance_name = f"{percount['prefix']}{i}_{base_name}"
                    detector = self.LoadDetector(detector_type=base_name, name=instance_name, schema_args=percount, trigger_callback=trigger_callback, count_index=i)
                    if detector is not None:
                        self.RegisterExtractor(registry=registry, extractor=detector, iter_mode=iter_mode)

    def LoadToFeatureRegistry(self, schema:GameSchema, registry:FeatureRegistry) -> None:
        iter_mode = IterationMode.AGGREGATE
        for base_name,aggregate in schema.AggregateFeatures.items():
            if self._game_schema.FeatureEnabled(feature_name=base_name, iter_mode=iter_mode, extract_mode=self._mode, overrides=self._overrides):
                feature = self.LoadFeature(feature_type=base_name, name=base_name, schema_args=aggregate)
                if feature is not None:
                    self.RegisterExtractor(registry=registry, extractor=feature, iter_mode=iter_mode)
        iter_mode = IterationMode.PERCOUNT
        for base_name,percount in schema.PerCountFeatures.items():
            if self._game_schema.FeatureEnabled(feature_name=base_name, iter_mode=iter_mode, extract_mode=self._mode, overrides=self._overrides):
                for i in ExtractorLoader._genCountRange(count=percount["count"], schema=schema):
                    instance_name = f"{percount['prefix']}{i}_{base_name}"
                    feature = self.LoadFeature(feature_type=base_name, name=instance_name, schema_args=percount)
                    if feature is not None:
                        self.RegisterExtractor(registry=registry, extractor=feature, iter_mode=iter_mode)

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
