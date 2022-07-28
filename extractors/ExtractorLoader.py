# import libraries
import abc
import logging
from importlib import import_module
from typing import Any, Callable, Dict, List, Optional, Type
# import locals
from extractors.Extractor import Extractor, ExtractorParameters
from extractors.ExtractorRegistry import ExtractorRegistry
from extractors.detectors.Detector import Detector
from extractors.detectors.DetectorRegistry import DetectorRegistry
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

        # bit of a hack using globals() here, but theoretically this lets us access the class object with only a string.
        # feature_class : Optional[Type[Extractor]] = globals().get(feature_type, None)
        feature_module = import_module(f"games.{self._game_schema.GameName}.features.{feature_type}")
        feature_class : Optional[Type[Extractor]] = getattr(feature_module, feature_type)
        if feature_class is not None:
            if self._mode in feature_class.AvailableModes():
                Logger.Log(f"{self._mode} was found in AvailableModes for {feature_class}: [{feature_class.AvailableModes()}].")
                params = ExtractorParameters(name=name, description=schema_args.get('description',""), mode=self._mode, count_index=count_index)
                try:
                    ret_val = self._loadFeature(feature_type=feature_type, extractor_params=params, schema_args=schema_args)
                except NotImplementedError as err:
                    Logger.Log(f"In ExtractorLoader, '{name}' was not loaded due to an error:", logging.ERROR)
                    Logger.Log(str(err), logging.ERROR, depth=1)
            else:
                Logger.Log(f"{self._mode} was not in AvailableModes for {feature_class}, we are skipping the loading of this feature.")
        else:
            Logger.Log(f"Could not find {feature_type} in globals()!", logging.WARN)

        return ret_val

    def RegisterExtractor(self, registry:ExtractorRegistry, extractor:Extractor, iter_mode:IterationMode):
        if self._mode in extractor.AvailableModes():
            registry.Register(extractor=extractor, mode=iter_mode)

    def LoadToDetectorRegistry(self, registry:DetectorRegistry, trigger_callback:Callable[[Event], None]) -> None:
        # first, load aggregate detectors
        iter_mode = IterationMode.AGGREGATE
        for base_name,aggregate in self._game_schema.AggregateDetectors.items():
            if self._game_schema.DetectorEnabled(detector_name=base_name, iter_mode=iter_mode, extract_mode=self._mode, overrides=self._overrides):
                detector_type = aggregate.get('detector_type', base_name) # try to get 'detector type' from aggregate, if it's not there default to name of the config item.
                detector = self.LoadDetector(detector_type=detector_type, name=base_name, schema_args=aggregate, trigger_callback=trigger_callback)
                if detector is not None:
                    self.RegisterExtractor(registry=registry, extractor=detector, iter_mode=iter_mode)
        # second, load iterated (per-count) detectors
        iter_mode = IterationMode.PERCOUNT
        for base_name,percount in self._game_schema.PerCountDetectors.items():
            if self._game_schema.DetectorEnabled(detector_name=base_name, iter_mode=iter_mode, extract_mode=self._mode, overrides=self._overrides):
                detector_type = percount.get('detector_type', base_name) # try to get 'detector type' from percount config, if it's not there default to name of the config item.
                for i in ExtractorLoader._genCountRange(count=percount["count"], schema=self._game_schema):
                    instance_name = f"{percount['prefix']}{i}_{base_name}"
                    detector = self.LoadDetector(detector_type=detector_type, name=instance_name, schema_args=percount, trigger_callback=trigger_callback, count_index=i)
                    if detector is not None:
                        self.RegisterExtractor(registry=registry, extractor=detector, iter_mode=iter_mode)

    def LoadToFeatureRegistry(self, registry:FeatureRegistry) -> None:
        iter_mode = IterationMode.AGGREGATE
        for base_name,aggregate in self._game_schema.AggregateFeatures.items():
            if self._game_schema.FeatureEnabled(feature_name=base_name, iter_mode=iter_mode, extract_mode=self._mode, overrides=self._overrides):
                feature_type = aggregate.get('feature_type', base_name) # try to get 'feature type' from aggregate, if it's not there default to name of the config item.
                feature = self.LoadFeature(feature_type=feature_type, name=base_name, schema_args=aggregate)
                if feature is not None:
                    self.RegisterExtractor(registry=registry, extractor=feature, iter_mode=iter_mode)
        iter_mode = IterationMode.PERCOUNT
        for base_name,percount in self._game_schema.PerCountFeatures.items():
            if self._game_schema.FeatureEnabled(feature_name=base_name, iter_mode=iter_mode, extract_mode=self._mode, overrides=self._overrides):
                feature_type = percount.get('feature_type', base_name) # try to get 'feature type' from percount, if it's not there default to name of the config item.
                for i in ExtractorLoader._genCountRange(count=percount["count"], schema=self._game_schema):
                    instance_name = f"{percount['prefix']}{i}_{base_name}"
                    feature = self.LoadFeature(feature_type=feature_type, name=instance_name, schema_args=percount, count_index=i)
                    if feature is not None:
                        self.RegisterExtractor(registry=registry, extractor=feature, iter_mode=iter_mode)
        # for firstOrder in registry.FirstOrdersRequested():
        #     #TODO load firstOrder, if it's not loaded already
        #     if not firstOrder in registry.GetExtractorNames():


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
