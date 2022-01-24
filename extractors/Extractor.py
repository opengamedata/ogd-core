## import standard libraries
import abc
import logging
from typing import Any, Dict, List, Type, Union
from extractors.FeatureLoader import FeatureLoader
from extractors.FeatureRegistry import FeatureRegistry
# Local imports
import utils
from managers.Request import ExporterTypes
from schemas.GameSchema import GameSchema
from schemas.Event import Event

## @class Extractor
class Extractor(abc.ABC):

    # *** ABSTRACTS ***

    ## Abstract declaration of a function to get the names of all features.
    @abc.abstractmethod
    def GetFeatureNames(self) -> List[str]:
        pass

    ## Abstract declaration of a function to get the calculated value of the feature, given data seen so far.
    @abc.abstractmethod
    def GetFeatureValues(self, export_types:ExporterTypes) -> Dict[str,List[Any]]:
        pass

    ## Abstract declaration of a function to get the calculated value of the feature, given data seen so far.
    @abc.abstractmethod
    def ProcessEvent(self, event: Event):
        pass

    @abc.abstractmethod
    def _prepareLoader(self) -> FeatureLoader:
        pass

    # *** PUBLIC BUILT-INS ***

    def __init__(self, LoaderClass:Type[FeatureLoader], game_schema: GameSchema,
                 feature_overrides:Union[List[str],None]=None):
        self._game_schema : GameSchema            = game_schema
        self._overrides   : Union[List[str],None] = feature_overrides
        self._LoaderClass : Type[FeatureLoader]   = LoaderClass
        self._loader      : FeatureLoader         = self._prepareLoader()
        self._registry    : FeatureRegistry       = self._prepareRegistry()
    def __str__(self):
        return f""

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    ##  Function to empty the list of lines stored by the PopulationProcessor.
    #   This is helpful if we're processing a lot of data and want to avoid
    #   eating too much memory.
    def ClearLines(self):
        utils.Logger.toStdOut(f"Clearing population entries from PopulationProcessor.", logging.DEBUG)
        self._registry = self._prepareRegistry()

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
    def _prepareRegistry(self):
        return FeatureRegistry(loader=self._loader, game_schema=self._game_schema, feature_overrides=self._overrides)
