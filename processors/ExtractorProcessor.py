## import standard libraries
import abc
from typing import Dict, List, Type, Optional, Set

from numpy import isin
# import locals
from extractors.registries.ExtractorRegistry import ExtractorRegistry
from extractors.ExtractorLoader import ExtractorLoader
from schemas.FeatureData import FeatureData
from extractors.ExtractorLoader import ExtractorLoader
from extractors.registries.FeatureRegistry import FeatureRegistry
from processors.Processor import Processor
from schemas.ExtractionMode import ExtractionMode
from schemas.GameSchema import GameSchema
from schemas.ExportMode import ExportMode
from utils import ExportRow

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

    @abc.abstractmethod
    def _clearLines(self) -> None:
        pass

    # *** BUILT-INS ***

    def __init__(self, LoaderClass:Type[ExtractorLoader], game_schema: GameSchema, feature_overrides:Optional[List[str]]=None):
        super().__init__(game_schema=game_schema, feature_overrides=feature_overrides)
        self._LoaderClass : Type[ExtractorLoader] = LoaderClass
        self._loader      : ExtractorLoader       = LoaderClass(player_id=self._playerID, session_id=self._sessionID, game_schema=self._game_schema,
                                                                mode=self._mode, feature_overrides=self._overrides)
        self._overrides   : Optional[List[str]]   = feature_overrides
        self._registry    : Optional[ExtractorRegistry] = None

    def __str__(self):
        return f""

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def ProcessFeatureData(self, feature_list:List[FeatureData]) -> None:
        if self._registry is not None:
            for feature in feature_list:
                self._registry.ExtractFromFeatureData(feature=feature)
        else:
            Logger.Log(f"Processor has no registry, skipping FeatureData.", logging.WARN)

    def GetExtractorNames(self) -> List[str]:
        # TODO: add error handling code, if applicable.
        return self._getExtractorNames()

    def ClearLines(self):
        self._clearLines()

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
