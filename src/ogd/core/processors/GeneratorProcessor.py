## import standard libraries
import abc
import logging
from typing import List, Type, Optional
# import locals
from ogd.core.registries.GeneratorRegistry import GeneratorRegistry
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.configs.generators.GeneratorCollectionConfig import GeneratorCollectionConfig
from ogd.core.processors.Processor import Processor
from ogd.common.models.Feature import Feature
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.utils.Logger import Logger

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

    def __init__(self, generator_cfg:GeneratorCollectionConfig, LoaderClass:Type[GeneratorLoader], feature_overrides:Optional[List[str]]=None):
        super().__init__(generator_cfg=generator_cfg)
        self._overrides   : Optional[List[str]]   = feature_overrides
        self._loader      : GeneratorLoader       = LoaderClass(player_id=self._playerID, session_id=self._sessionID, generator_config=self._generator_cfg,
                                                                mode=self._mode, feature_overrides=self._overrides)
        self._registry    : Optional[GeneratorRegistry] = None # Set to 0, let subclasses create own instances.

    @property
    def GeneratorNames(self) -> List[str]:
        # TODO: add error handling code, if applicable.
        return self._getGeneratorNames()

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def ProcessFeature(self, feature_list:List[Feature]) -> None:
        if self._registry is not None:
            for feature in feature_list:
                self._registry.UpdateFromFeature(feature=feature)
        else:
            Logger.Log("Processor has no registry, skipping Feature.", logging.WARN)

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
