## import standard libraries
import abc
import logging
from typing import Dict, List, Type, Optional, Set
# import locals
from ogd.core.registries.GeneratorRegistry import GeneratorRegistry
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.models.FeatureData import FeatureData
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.processors.Processor import Processor
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.schemas.games.GameSchema import GameSchema
from ogd.core.models.enums.ExportMode import ExportMode
from ogd.core.utils.Logger import Logger
from ogd.core.utils.utils import ExportRow

## @class Processor
class GeneratorProcessor(Processor):

    # *** ABSTRACTS ***

    ## Abstract declaration of a function to get the calculated value of the feature, given data seen so far.

    @property
    @abc.abstractmethod
    def _mode(self) -> ExtractionMode:
        pass

    ## Abstract declaration of a function to get the names of all features.
    @abc.abstractmethod
    def _getGeneratorNames(self) -> List[str]:
        pass

    @property
    @abc.abstractmethod
    def _playerID(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def _sessionID(self) -> str:
        pass

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, game_schema: GameSchema, LoaderClass:Type[GeneratorLoader], feature_overrides:Optional[List[str]]=None):
        super().__init__(game_schema=game_schema)
        self._overrides   : Optional[List[str]]   = feature_overrides
        self._loader      : GeneratorLoader       = LoaderClass(player_id=self._playerID, session_id=self._sessionID, game_schema=self._game_schema,
                                                                mode=self._mode, feature_overrides=self._overrides)
        self._registry    : Optional[GeneratorRegistry] = None # Set to 0, let subclasses create own instances.

    def __str__(self):
        return f""

    @property
    def GeneratorNames(self) -> List[str]:
        # TODO: add error handling code, if applicable.
        return self._getGeneratorNames()

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def ProcessFeatureData(self, feature_list:List[FeatureData]) -> None:
        if self._registry is not None:
            for feature in feature_list:
                self._registry.UpdateFromFeatureData(feature=feature)
        else:
            Logger.Log(f"Processor has no registry, skipping FeatureData.", logging.WARN)

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
