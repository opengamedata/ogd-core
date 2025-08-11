## import standard libraries
import abc
from typing import List, Type, Optional

# import locals
from ogd.common.models.Feature import Feature
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.configs.generators.GeneratorCollectionConfig import GeneratorCollectionConfig
from ogd.core.registries.ExtractorRegistry import ExtractorRegistry
from ogd.core.processors.GeneratorProcessor import GeneratorProcessor

## @class Processor
class ExtractorProcessor(GeneratorProcessor):

    # *** ABSTRACTS ***

    ## Abstract declaration of a function to get the calculated value of the feature, as a Feature package, given data seen so far.
    @abc.abstractmethod
    def _getFeatures(self, order:int) -> List[Feature]:
        pass

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, generator_cfg:GeneratorCollectionConfig, LoaderClass:Type[GeneratorLoader], feature_overrides:Optional[List[str]]=None):
        super().__init__(generator_cfg=generator_cfg, LoaderClass=LoaderClass, feature_overrides=feature_overrides)
        self._registry : ExtractorRegistry = ExtractorRegistry(mode=self._mode)
        self._registry.LoadGenerators(generator_cfg=generator_cfg, loader=self._loader, overrides=feature_overrides)

    def __str__(self):
        return f""

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def GetFeatures(self, order:int) -> List[Feature]:
        # TODO: add error handling code, if applicable.
        return self._getFeatures(order=order)

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
