## import standard libraries
import abc
from typing import List, Type, Optional

# import locals
from ogd.common.models.FeatureSet import FeatureSet
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.configs.generators.GeneratorCollectionConfig import GeneratorCollectionConfig
from ogd.core.registries.ExtractorRegistry import ExtractorRegistry
from ogd.core.processors.GeneratorProcessor import GeneratorProcessor

## @class Processor
class ExtractorProcessor(GeneratorProcessor):

    # *** ABSTRACTS ***

    ## Abstract declaration of a function to get the calculated value of the feature, as a Feature package, given data seen so far.
    @abc.abstractmethod
    def _getFeatures(self, order:Optional[int], app_id:Optional[str]=None) -> FeatureSet:
        pass

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, generator_cfg:GeneratorCollectionConfig, LoaderClass:Type[GeneratorLoader], feature_overrides:Optional[List[str]]=None):
        super().__init__(generator_cfg=generator_cfg, LoaderClass=LoaderClass, feature_overrides=feature_overrides)
        self._registry : ExtractorRegistry = ExtractorRegistry(mode=self._mode)
        self._registry.LoadGenerators(generator_cfg=generator_cfg, loader=self._loader, overrides=feature_overrides)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def GetFeatures(self, order:Optional[int], app_id:Optional[str]=None) -> FeatureSet:
        """Get a FeatureSet with the feature outputs of all Extractors for the given order, or all Features from all orders if the order parameter is None

        :param order: _description_
        :type order: Optional[int]
        :param app_id: _description_
        :type app_id: str
        :return: _description_
        :rtype: FeatureSet
        """
        # TODO: add error handling code, if applicable.
        return self._getFeatures(order=order, app_id=app_id)

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
