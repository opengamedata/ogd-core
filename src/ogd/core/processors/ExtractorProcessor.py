## import standard libraries
import abc
from typing import Dict, List, Type, Optional, Set

# import locals
from ogd.core.models.FeatureData import FeatureData
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.registries.ExtractorRegistry import ExtractorRegistry
from ogd.core.processors.GeneratorProcessor import GeneratorProcessor
from ogd.core.schemas.games.GameSchema import GameSchema
from ogd.core.models.enums.ExportMode import ExportMode
from ogd.core.utils.utils import ExportRow

## @class Processor
class ExtractorProcessor(GeneratorProcessor):

    # *** ABSTRACTS ***

    ## Abstract declaration of a function to get the calculated value of the feature, as a FeatureData package, given data seen so far.
    @abc.abstractmethod
    def _getFeatureData(self, order:int) -> List[FeatureData]:
        pass

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, game_schema: GameSchema, LoaderClass:Type[GeneratorLoader], feature_overrides:Optional[List[str]]=None):
        super().__init__(game_schema=game_schema, LoaderClass=LoaderClass, feature_overrides=feature_overrides)
        self._registry : ExtractorRegistry = ExtractorRegistry(mode=self._mode)
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
