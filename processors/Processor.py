## import standard libraries
import abc
import logging
from typing import Any, Dict, List, Type, Union
# import locals
from utils import Logger
from features.FeatureLoader import FeatureLoader
from features.FeatureRegistry import FeatureRegistry
from features.FeatureData import FeatureData
from schemas.GameSchema import GameSchema
from schemas.Event import Event
from schemas.Request import ExporterTypes

## @class Processor
class Processor(abc.ABC):

    # *** ABSTRACTS ***

    ## Abstract declaration of a function to get the names of all features.
    @abc.abstractmethod
    def _getFeatureNames(self) -> List[str]:
        pass

    ## Abstract declaration of a function to get the calculated value of the feature, given data seen so far.
    @abc.abstractmethod
    def _getFeatureValues(self, export_types:ExporterTypes, as_str:bool=False) -> Dict[str,List[Any]]:
        pass

    @abc.abstractmethod
    def _getFeatureData(self, order:int) -> Dict[str,List[FeatureData]]:
        pass

    ## Abstract declaration of a function to get the calculated value of the feature, given data seen so far.
    @abc.abstractmethod
    def _processEvent(self, event:Event) -> None:
        pass

    @abc.abstractmethod
    def _processFeatureData(self, feature:FeatureData) -> None:
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
        self._loader.LoadToFeatureRegistry(registry=self._registry)
    def __str__(self):
        return f""

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def GetFeatureNames(self) -> List[str]:
        # TODO: add error handling code, if applicable.
        return self._getFeatureNames()

    def GetFeatureValues(self, export_types:ExporterTypes, as_str:bool=False) -> Dict[str,List[Any]]:
        # TODO: add error handling code, if applicable.
        return self._getFeatureValues(export_types=export_types, as_str=as_str)

    def GetFeatureData(self, order:int) -> Dict[str,List[FeatureData]]:
        # TODO: add error handling code, if applicable.
        return self._getFeatureData(order=order)

    def ProcessEvent(self, event:Event) -> None:
        # TODO: add error handling code, if applicable.
        self._processEvent(event=event)

    def ProcessFeatureData(self, feature:FeatureData) -> None:
        # TODO: add error handling code, if applicable.
        self._processFeatureData(feature=feature)

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
