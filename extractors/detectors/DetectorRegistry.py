## import standard libraries
import enum
import logging
from collections import OrderedDict
from datetime import datetime
from typing import Any, Callable, List, Optional
## import local files
from extractors.detectors.Detector import Detector
from extractors.Extractor import Extractor
from extractors.ExtractorRegistry import ExtractorRegistry
from schemas.Event import Event
from schemas.FeatureData import FeatureData
from schemas.IterationMode import IterationMode

## @class Extractor
#  Abstract base class for game feature extractors.
#  Gives a few static functions to be used across all extractor classes,
#  and defines an interface that the SessionProcessor can use.
class DetectorRegistry(ExtractorRegistry):
    """Class for registering features to listen for events.

    :return: [description]
    :rtype: [type]
    """

    # *** BUILT-INS ***

    # Base constructor for Registry.
    def __init__(self):
        """Base constructor for Registry

        Just sets up mostly-empty dictionaries for use by the registry.
        """
        super().__init__()
        self._detectors      : OrderedDict[str, Detector]                = OrderedDict()

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
    def to_string(self, num_lines:Optional[int] = None) -> str:
        """Alternate string conversion for Extractors, with limitable number of lines.

        Creates a list of features in the extractor, separated by newlines.
        Optional num_lines param allows the function caller to limit number of lines in the string.
        :param num_lines: Max number of lines to include in the string.
        If None, then include all strings, defaults to None
        :type num_lines:  Optional[int], optional
        :return: A string with line-separated stringified features.
        :rtype: str
        """
        ret_val : List[str] = []
        ret_val = [str(feat) for feat in self._detectors.values()]
        if num_lines is None:
            return '\n'.join(ret_val)
        else:
            return '\n'.join(ret_val[:num_lines])

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _register(self, extractor:Extractor, mode:IterationMode):
        if isinstance(extractor, Detector):
            _listener = ExtractorRegistry.Listener(name=extractor.Name, mode=mode)
            _event_types   = extractor.GetEventDependencies()
            # First, add detector to the _features dict.
            self._detectors[extractor.Name] = extractor
            # Register detector's requested events.
            if "all_events" in _event_types:
                self._event_registry["all_events"].append(_listener)
            else:
                for event in _event_types:
                    if event not in self._event_registry.keys():
                        self._event_registry[event] = []
                    self._event_registry[event].append(_listener)
        else:
            raise TypeError("DetectorRegistry was given an Extractor which was not a Detector!")

    def _extractFromEvent(self, event:Event) -> None:
        """Perform extraction of features from a row.

        :param event: [description]
        :type event: Event
        :param table_schema: A data structure containing information on how the db
                             table assiciated with this game is structured.
        :type table_schema: TableSchema
        """
        if event.EventName in self._event_registry.keys():
            # send event to every listener for the given event name.
            for listener in self._event_registry[event.EventName]:
                if listener.name in self._detectors.keys():
                    self._detectors[listener.name].ExtractFromEvent(event)
        # don't forget to send to any features listening for "all" events
        for listener in self._event_registry["all_events"]:
            if listener.name in self._detectors.keys():
                self._detectors[listener.name].ExtractFromEvent(event)

    def _extractFromFeatureData(self, feature:FeatureData) -> None:
        return

    def _getExtractorNames(self) -> List[str]:
        """Implementation of abstract function to retrieve the names of all extractors currently registered.

        :return: A list of all currently-registered detectors.
        :rtype: List[str]
        """
        ret_val : List[str] = [feature.Name for feature in self._detectors.values()]
        return ret_val

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

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
