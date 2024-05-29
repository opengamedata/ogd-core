# import libraries
import abc
import logging
from importlib import import_module
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Type
# import locals
from ogd.core.generators.extractors import builtin
from ogd.core.generators.extractors.builtin.BuiltinExtractor import BuiltinExtractor
from ogd.core.generators.extractors.builtin import *
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
    def _loadDetector(self, detector_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any], trigger_callback:Callable[[Event], None]) -> Optional[Detector]:
        pass

    @staticmethod
    @abc.abstractmethod
    def _getFeaturesModule() -> ModuleType:
        pass

    # *** BUILT-INS & PROPERTIES ***

    _derived_builtins : Dict[str, Type[BuiltinExtractor]] = {}
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
        # TODO : seems like Loader shouldn't really need player ID and session ID, consider removing.
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
        ret_val = self._loadDetector(detector_type=detector_type, extractor_params=params, schema_args=schema_args, trigger_callback=trigger_callback) \
               or self._loadBuiltinDetector(detector_type=detector_type, extractor_params=params, schema_args=schema_args, trigger_callback=trigger_callback)

        return ret_val

    def LoadFeature(self, feature_type:str, name:str, schema_args:Dict[str,Any], count_index:Optional[int] = None) -> Optional[Extractor]:
        ret_val = None

        if self._validateMode(feature_type=feature_type):
            params = GeneratorParameters(name=name, description=schema_args.get('description',""), mode=self._mode, count_index=count_index)
            ret_val = self._loadFeature(feature_type=feature_type, extractor_params=params, schema_args=schema_args) \
                   or self._loadBuiltinFeature(feature_type=feature_type, extractor_params=params, schema_args=schema_args)

        return ret_val

    def GetFeatureClass(self, feature_type:str) -> Optional[Type[Extractor]]:
        ret_val : Optional[Type[Extractor]] = None
        game_module = self._getFeaturesModule()
        try:
            # Try to find feature module in the game module, falling back on finding it in builtin module.
            feature_mod = getattr(game_module, feature_type, getattr(builtin, feature_type))
        except NameError as err:
            Logger.Log(f"Could not find class {feature_type} in module `{game_module}` or in `builtin`, a NameError occurred:\n{err}\nSearching `builtin` module instead.", logging.WARN)
        else:
            # If the above did not generate an error, then try to get actual feature class from its module.
            # If not found, then we fall back on getting builtin directly, though in practice this is probably redundant.
            ret_val = getattr(feature_mod, feature_type, self.GetBuiltinFeatureClass(feature_type=feature_type))
        finally:
            return ret_val

    def GetBuiltinFeatureClass(self, feature_type:str) -> Optional[Type[BuiltinExtractor]]:
        ret_val : Optional[Type[BuiltinExtractor]] = None
        try:
            feature_mod = getattr(builtin, feature_type)
            ret_val = getattr(feature_mod, feature_type)
        except NameError as err:
            Logger.Log(f"Could not find class {feature_type} in module game module or `builtin`, a NameError occurred:\n{err}", logging.WARN)
        finally:
            return ret_val

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _validateMode(self, feature_type) -> bool:
        ret_val = False

        feature_class : Optional[Type[Extractor]]  = self.GetFeatureClass(feature_type=feature_type)
        if feature_class is not None:
            ret_val = self._mode in feature_class.AvailableModes()
        else:
            Logger.Log(f"In GeneratorLoader, skipping feature class `{feature_type}`, which could not be found.", logging.WARN)

        return ret_val

    def _loadBuiltinFeature(self, feature_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any]) -> Extractor:
        ret_val : BuiltinExtractor
        if extractor_params._name not in GeneratorLoader._derived_builtins.keys():
            feature_class = self.GetBuiltinFeatureClass(feature_type=feature_type)
            if feature_class is not None:
                GeneratorLoader._derived_builtins[extractor_params._name] = feature_class._createDerivedGenerator(params=extractor_params, schema_args=schema_args)
        # Session-level features.
        if extractor_params._name in GeneratorLoader._derived_builtins.keys():
            ret_val = GeneratorLoader._derived_builtins[extractor_params._name](params=extractor_params, schema_args=schema_args)
        else:
            raise NotImplementedError(f"'{feature_type}' is not a valid built-in feature.")
        return ret_val

    def _loadBuiltinDetector(self, detector_type:str, extractor_params:GeneratorParameters, schema_args:Dict[str,Any], trigger_callback:Callable[[Event], None]) -> Detector:
        raise NotImplementedError(f"'{detector_type}' is not a valid built-in detector.")
