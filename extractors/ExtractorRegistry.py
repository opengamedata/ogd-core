## import standard libraries
import abc
import enum
import logging
from collections import OrderedDict
from typing import Dict, List
## import local files
from utils import Logger
from extractors.Extractor import Extractor
from schemas.FeatureData import FeatureData
from schemas.Event import Event

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
        @enum.unique
        class Kinds(enum.Enum):
            AGGREGATE = enum.auto()
            PERCOUNT  = enum.auto()

        def __init__(self, name:str, kind:Kinds):
            self.name = name
            self.kind = kind
        
        def __str__(self) -> str:
            return f"{self.name} ({'aggregate' if self.kind == ExtractorRegistry.Listener.Kinds.AGGREGATE else 'per-count'})"

        def __repr__(self) -> str:
            return str(self)

    # *** ABSTRACTS ***

    @abc.abstractmethod
    def _register(self, extractor:Extractor, kind:Listener.Kinds):
        pass

    @abc.abstractmethod
    def _getExtractorNames(self) -> List[str]:
        pass

    @abc.abstractmethod
    def _extractFromEvent(self, event:Event) -> None:
        pass

    @abc.abstractmethod
    def _extractFromFeatureData(self, feature:FeatureData) -> None:
        pass

    # *** BUILT-INS ***

    # Base constructor for Registry.
    def __init__(self):
        """Base constructor for Registry

        Just sets up mostly-empty dictionaries for use by the registry.
        _features is a list of feature orders, where each element is a map from feature names to actual Feature instances.
        _event_registry maps event names to Listener objects, which basically just say which feature(s) wants the given enent.
        _feature_registry maps feature names to Listener objects, which basically just say which 2nd-order feature(s) wants the given 1st-order feature.
        """
        self._event_registry : Dict[str,List[ExtractorRegistry.Listener]] = {"all_events":[]}
        self._feature_registry: Dict[str,List[ExtractorRegistry.Listener]] = {}

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def Register(self, extractor:Extractor, kind:Listener.Kinds):
        self._register(extractor=extractor, kind=kind)

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
        self._extractFromFeatureData(feature=feature)

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
