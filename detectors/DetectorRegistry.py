## import standard libraries
import enum
import logging
from collections import OrderedDict
from datetime import datetime
from typing import Any, Callable, Dict, List, Union
## import local files
from utils import Logger
from Detector import Detector
from schemas.Event import Event

## @class Extractor
#  Abstract base class for game feature extractors.
#  Gives a few static functions to be used across all extractor classes,
#  and defines an interface that the SessionProcessor can use.
class DetectorRegistry:
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
            return f"{self.name} ({'aggregate' if self.kind == DetectorRegistry.Listener.Kinds.AGGREGATE else 'per-count'})"

        def __repr__(self) -> str:
            return str(self)

    @enum.unique
    class FeatureOrders(enum.Enum):
        FIRST_ORDER = 0
        SECOND_ORDER = 1

    # *** BUILT-INS ***

    # Base constructor for Registry.
    def __init__(self, trigger_callback:Callable[[Event], None]):
        """Base constructor for Registry

        Just sets up mostly-empty dictionaries for use by the registry.
        """
        self._trigger_callback = trigger_callback
        self._detectors      : OrderedDict[str, Detector]                = OrderedDict()
        self._event_registry : Dict[str,List[DetectorRegistry.Listener]] = {"all_events":[]}

    # string conversion for Extractors.
    def __str__(self) -> str:
        """string conversion for Extractors.

        Creates a list of all features in the extractor, separated by newlines.
        :return: A string with line-separated stringified features.
        :rtype: str
        """
        ret_val : List[str] = []
        ret_val = [str(feat) for feat in self._detectors.values()]
        return '\n'.join(ret_val)

    # Alternate string conversion for Extractors, with limitable number of lines.
    def to_string(self, num_lines:Union[int,None] = None) -> str:
        """Alternate string conversion for Extractors, with limitable number of lines.

        Creates a list of features in the extractor, separated by newlines.
        Optional num_lines param allows the function caller to limit number of lines in the string.
        :param num_lines: Max number of lines to include in the string.
        If None, then include all strings, defaults to None
        :type num_lines:  Union[int,None], optional
        :return: A string with line-separated stringified features.
        :rtype: str
        """
        ret_val : List[str] = []
        ret_val = [str(feat) for feat in self._detectors.values()]
        if num_lines is None:
            return '\n'.join(ret_val)
        else:
            return '\n'.join(ret_val[:num_lines])

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***
    def ExtractFromEvent(self, event:Event) -> None:
        """Perform extraction of features from a row.

        :param event: [description]
        :type event: Event
        :param table_schema: A data structure containing information on how the db
                             table assiciated with this game is structured.
        :type table_schema: TableSchema
        """
        if event.event_name in self._event_registry.keys():
            # send event to every listener for the given event name.
            for listener in self._event_registry[event.event_name]:
                if listener.name in self._detectors.keys():
                    self._detectors[listener.name].ExtractFromEvent(event)
        # don't forget to send to any features listening for "all" events
        for listener in self._event_registry["all_events"]:
            if listener.name in self._detectors.keys():
                self._detectors[listener.name].ExtractFromEvent(event)

    def GetDetectorNames(self) -> List[str]:
        """Function to generate a list names of all enabled features, given a GameSchema
        This is different from the feature_names() function of GameSchema,
        which ignores the 'enabled' attribute and does not expand per-count features
        (e.g. this function would include 'lvl0_someFeat', 'lvl1_someFeat', 'lvl2_someFeat', etc.
        while feature_names() only would include 'someFeat').

        :param schema: The schema from which feature names should be generated.
        :type schema: GameSchema
        :return: A list of feature names.
        :rtype: List[str]
        """
        ret_val : List[str] = [feature.Name() for feature in self._detectors.values()]
        return ret_val

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def Register(self, detector:Detector, kind:Listener.Kinds):
        _listener = DetectorRegistry.Listener(name=detector.Name(), kind=kind)
        _event_types   = detector.GetEventDependencies()
        # First, add detector to the _features dict.
        self._detectors[detector.Name()] = detector
        # Register detector's requested events.
        if "all_events" in _event_types:
            self._event_registry["all_events"].append(_listener)
        else:
            for event in _event_types:
                if event not in self._event_registry.keys():
                    self._event_registry[event] = []
                self._event_registry[event].append(_listener)

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
