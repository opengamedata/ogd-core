# import libraries
import abc
import logging
from importlib import import_module
from typing import Any, Callable, Dict, List, Optional, Type
# import locals
from ogd.core.generators.Generator import Generator, GeneratorParameters
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode
from ogd.core.schemas.games.GameSchema import GameSchema
from ogd.core.utils.Logger import Logger

class GeneratorLoader(abc.ABC):

    # *** ABSTRACTS ***
    
    @abc.abstractmethod
    def _loadFeature(self, feature_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any]) -> Extractor:
        pass
    
    @abc.abstractmethod
    def _loadDetector(self, detector_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any], trigger_callback:Callable[[Event], None]) -> Detector:
        pass

    @staticmethod
    @abc.abstractmethod
    def _getFeaturesModule():
        pass

    # *** BUILT-INS & PROPERTIES ***

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

        params = GeneratorParameters(name=name, description=schema_args.get('description',""), mode=self._mode, count_index=count_index)
        try:
            ret_val = self._loadDetector(detector_type=detector_type, extractor_params=params, schema_args=schema_args, trigger_callback=trigger_callback)
        except NotImplementedError as err:
            Logger.Log(f"In GeneratorLoader, '{name}' is not a valid detector for {self._game_schema.GameName}", logging.ERROR)

        return ret_val

    def LoadFeature(self, feature_type:str, name:str, schema_args:Dict[str,Any], count_index:Optional[int] = None) -> Optional[Extractor]:
        ret_val = None

        if self._validateMode(feature_type=feature_type):
            params = GeneratorParameters(name=name, description=schema_args.get('description',""), mode=self._mode, count_index=count_index)
            try:
                ret_val = self._loadFeature(feature_type=feature_type, extractor_params=params, schema_args=schema_args)
            except NotImplementedError as err:
                Logger.Log(f"In GeneratorLoader, unable to load '{name}', {feature_type} is not implemented!:", logging.ERROR)
                Logger.Log(str(err), logging.ERROR, depth=1)

        return ret_val

    def GetFeatureClass(self, feature_type:str) -> Optional[Type[Extractor]]:
        ret_val : Optional[Type[Extractor]] = None
        base_mod = self._getFeaturesModule()
        try:
            feature_mod = getattr(base_mod, feature_type)
            ret_val     = getattr(feature_mod, feature_type)
        except NameError as err:
            Logger.Log(f"Could not get class {feature_type}, a NameError occurred:\n{err}", logging.WARN)
        finally:
            return ret_val

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _validateMode(self, feature_type) -> bool:
        ret_val = False

        mod_name = f"ogd.games.{self._game_schema.GameName}.features.{feature_type}"
        try:
            feature_module = import_module(mod_name)
        except ModuleNotFoundError:
            Logger.Log(f"In GeneratorLoader, '{mod_name}' could not be found, skipping {feature_type}", logging.ERROR)
        else:
            # bit of a hack using globals() here, but theoretically this lets us access the class object with only a string.
            # feature_class : Optional[Type[Extractor]] = globals().get(feature_type, None)
            feature_class : Optional[Type[Extractor]] = getattr(feature_module, feature_type, None)
            if feature_class is not None:
                ret_val = self._mode in feature_class.AvailableModes()
            else:
                Logger.Log(f"In GeneratorLoader, feature class '{feature_type}' could not be found in module {feature_module}", logging.WARN)

        return ret_val
