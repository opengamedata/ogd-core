## import standard libraries
import abc
import logging
from typing import Dict, List, Type, Optional, Set
# import locals
from extractors.registries.ExtractorRegistry import ExtractorRegistry
from extractors.ExtractorLoader import ExtractorLoader
from schemas.FeatureData import FeatureData
from extractors.ExtractorLoader import ExtractorLoader
from extractors.registries.FeatureRegistry import FeatureRegistry
from processors.Processor import Processor
from schemas.ExtractionMode import ExtractionMode
from schemas.games.GameSchema import GameSchema
from schemas.ExportMode import ExportMode
from utils.Logger import Logger
from utils.utils import ExportRow

## @class Processor
class ExtractorProcessor(Processor):

    # *** ABSTRACTS ***

    ## Abstract declaration of a function to get the calculated value of the feature, given data seen so far.

    @property
    @abc.abstractmethod
    def _mode(self) -> ExtractionMode:
        pass

    ## Abstract declaration of a function to get the names of all features.
    @abc.abstractmethod
    def _getExtractorNames(self) -> List[str]:
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

    def __init__(self, game_schema: GameSchema, LoaderClass:Type[ExtractorLoader], feature_overrides:Optional[List[str]]=None):
        super().__init__(game_schema=game_schema)
        self._LoaderClass : Type[ExtractorLoader] = LoaderClass
        self._overrides   : Optional[List[str]]   = feature_overrides
        self._loader      : ExtractorLoader       = LoaderClass(player_id=self._playerID, session_id=self._sessionID, game_schema=self._game_schema,
                                                                mode=self._mode, feature_overrides=self._overrides)
        self._registry    : Optional[ExtractorRegistry] = None

    def __str__(self):
        return f""

    @property
    def ExtractorNames(self) -> List[str]:
        # TODO: add error handling code, if applicable.
        return self._getExtractorNames()

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def ProcessFeatureData(self, feature_list:List[FeatureData]) -> None:
        if self._registry is not None:
            for feature in feature_list:
                self._registry.ExtractFromFeatureData(feature=feature)
        else:
            Logger.Log(f"Processor has no registry, skipping FeatureData.", logging.WARN)

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
