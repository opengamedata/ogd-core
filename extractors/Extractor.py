## import standard libraries
import abc
from typing import Any, Dict, List, Type, Union
# import locals
from features.FeatureLoader import FeatureLoader
from features.FeatureRegistry import FeatureRegistry
from features.FeatureData import FeatureData
from schemas.GameSchema import GameSchema
from schemas.Event import Event
from schemas.Request import ExporterTypes

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

    @abc.abstractmethod
    def GetFeatureData(self, order:int) -> Dict[str,List[FeatureData]]:
        pass

    ## Abstract declaration of a function to get the calculated value of the feature, given data seen so far.
    @abc.abstractmethod
    def ProcessEvent(self, event:Event):
        pass

    @abc.abstractmethod
    def ProcessFeatureData(self, feature:FeatureData):
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
        self._registry    : FeatureRegistry       = FeatureRegistry()
        self._loader      : FeatureLoader         = self._prepareLoader()
        self._loader.LoadToRegistry(registry=self._registry)
    def __str__(self):
        return f""

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
