## import standard libraries
import abc
from typing import Dict, List, Type, Optional, Set

from numpy import isin
# import locals
from schemas.FeatureData import FeatureData
from extractors.ExtractorLoader import ExtractorLoader
from extractors.registries.FeatureRegistry import FeatureRegistry
from processors.Processor import Processor
from schemas.GameSchema import GameSchema
from schemas.ExportMode import ExportMode
from utils import ExportRow

## @class Processor
class FeatureProcessor(Processor):

    # *** ABSTRACTS ***

    ## Abstract declaration of a function to get the calculated value of the feature, given data seen so far.
    @abc.abstractmethod
    def _getFeatureValues(self, as_str:bool=False) -> ExportRow:
        pass

    @abc.abstractmethod
    def _getFeatureData(self, order:int) -> List[FeatureData]:
        pass

    @abc.abstractmethod
    def _clearLines(self) -> None:
        pass

    # *** BUILT-INS ***

    def __init__(self, LoaderClass:Type[ExtractorLoader], game_schema: GameSchema,
                 feature_overrides:Optional[List[str]]=None):
        super().__init__(LoaderClass=LoaderClass, game_schema=game_schema, feature_overrides=feature_overrides)
        self._registry : FeatureRegistry = FeatureRegistry(mode=self._mode)
        self._registry.LoadFromSchema(schema=game_schema, loader=self._loader, overrides=feature_overrides)

    def __str__(self):
        return f""

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def GetFeatureValues(self, as_str:bool=False) -> ExportRow:
        # TODO: add error handling code, if applicable.
        return self._getFeatureValues(as_str=as_str)

    def GetFeatureData(self, order:int) -> List[FeatureData]:
        # TODO: add error handling code, if applicable.
        return self._getFeatureData(order=order)

    def ClearLines(self):
        self._clearLines()

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
