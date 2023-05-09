## import standard libraries
import abc
from typing import Dict, List, Type, Optional, Set

# import locals
from schemas.FeatureData import FeatureData
from extractors.ExtractorLoader import ExtractorLoader
from extractors.registries.FeatureRegistry import FeatureRegistry
from processors.ExtractorProcessor import ExtractorProcessor
from schemas.games.GameSchema import GameSchema
from schemas.ExportMode import ExportMode
from utils import ExportRow

## @class Processor
class FeatureProcessor(ExtractorProcessor):

    # *** ABSTRACTS ***

    ## Abstract declaration of a function to get the calculated value of the feature, as a FeatureData package, given data seen so far.
    @abc.abstractmethod
    def _getFeatureData(self, order:int) -> List[FeatureData]:
        pass

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, game_schema: GameSchema, LoaderClass:Type[ExtractorLoader], feature_overrides:Optional[List[str]]=None):
        super().__init__(game_schema=game_schema, LoaderClass=LoaderClass, feature_overrides=feature_overrides)
        self._registry : FeatureRegistry = FeatureRegistry(mode=self._mode)
        self._registry.LoadFromSchema(schema=game_schema, loader=self._loader, overrides=feature_overrides)

    def __str__(self):
        return f""

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def GetFeatureData(self, order:int) -> List[FeatureData]:
        # TODO: add error handling code, if applicable.
        return self._getFeatureData(order=order)

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
