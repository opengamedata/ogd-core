## import standard libraries
import abc
import logging
from typing import Any, Dict, List, Optional
from extractors.ExtractorLoader import ExtractorLoader
## import local files
from utils import Logger
from extractors.Extractor import Extractor
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
from schemas.GameSchema import GameSchema
from schemas.IterationMode import IterationMode

## @class Extractor
#  Abstract base class for game feature extractors.
#  Gives a few static functions to be used across all extractor classes,
#  and defines an interface that the SessionProcessor can use.
class ExtractorRegistry(abc.ABC):
    """Class for registering features to listen for events.

    :return: [description]
    :rtype: [type]
    """
    class Listener:
        def __init__(self, name:str, mode:IterationMode):
            self.name = name
            self.mode = mode
        
        def __str__(self) -> str:
            return f"{self.name} ({self.mode.name})"

        def __repr__(self) -> str:
            return str(self)

    # *** ABSTRACTS ***

    @abc.abstractmethod
    def _register(self, extractor:Extractor, iter_mode:IterationMode):
        pass

    @abc.abstractmethod
    def _getExtractorNames(self) -> List[str]:
        pass

    @abc.abstractmethod
    def _loadFromSchema(self, schema:GameSchema, loader:ExtractorLoader, overrides:Optional[List[str]]):
        pass

    @abc.abstractmethod
    def _extractFromEvent(self, event:Event) -> None:
        pass

    @abc.abstractmethod
    def _extractFromFeatureData(self, feature:FeatureData) -> None:
        pass

    # *** BUILT-INS & PROPERTIES ***

    # Base constructor for Registry.
    def __init__(self, mode:ExtractionMode):
        """Base constructor for Registry

        Just sets up mostly-empty dictionaries for use by the registry.
        _features is a list of feature orders, where each element is a map from feature names to actual Feature instances.
        _event_registry maps event names to Listener objects, which basically just say which feature(s) wants the given enent.
        _feature_registry maps feature names to Listener objects, which basically just say which 2nd-order feature(s) wants the given 1st-order feature.
        """
        self._event_registry : Dict[str,List[ExtractorRegistry.Listener]] = {"all_events":[]}
        self._mode        : ExtractionMode = mode

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def Register(self, extractor:Extractor, iter_mode:IterationMode):
        self._register(extractor=extractor, iter_mode=iter_mode)

    def GetExtractorNames(self) -> List[str]:
        """Function to generate a list names of all enabled features, given a GameSchema
        This is different from the FeatureNames property of GameSchema,
        which ignores the 'enabled' attribute and does not expand per-count features
        (e.g. this function would include 'lvl0_someFeat', 'lvl1_someFeat', 'lvl2_someFeat', etc.
        while FeatureNames only would include 'someFeat').

        :param schema: The schema from which feature names should be generated.
        :type schema: GameSchema
        :return: A list of feature names.
        :rtype: List[str]
        """
        return self._getExtractorNames()

    def LoadFromSchema(self, schema:GameSchema, loader:ExtractorLoader, overrides:Optional[List[str]]):
        self._loadFromSchema(schema=schema, loader=loader, overrides=overrides)

    def ExtractFromEvent(self, event:Event) -> None:
        """Perform extraction of features from a row.

        :param event: [description]
        :type event: Event
        :param table_schema: A data structure containing information on how the db
                             table assiciated with this game is structured.
        :type table_schema: TableSchema
        """
        self._extractFromEvent(event=event)

    def ExtractFromFeatureData(self, feature:FeatureData) -> None:
        """Perform extraction of features from a row.

        :param event: [description]
        :type event: Event
        :param table_schema: A data structure containing information on how the db
                             table assiciated with this game is structured.
        :type table_schema: TableSchema
        """
        if isinstance(feature, FeatureData):
            self._extractFromFeatureData(feature=feature)
        else:
            Logger.Log(f"Got an invalid feature {feature} of type {type(feature)} for a registry in {self._mode.name} mode")

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    # def _format(obj):
    #     if obj == None:
    #         return ""
    #     elif type(obj) is timedelta:
    #         total_secs = obj.total_seconds()
    #         # h = total_secs // 3600
    #         # m = (total_secs % 3600) // 60
    #         # s = (total_secs % 3600) % 60 // 1  # just for reference
    #         # return f"{h:02.0f}:{m:02.0f}:{s:02.3f}"
    #         return str(total_secs)
    #     if obj is None:
    #         return ''
    #     else:
    #         return str(obj)
