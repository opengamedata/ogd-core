## import standard libraries
import logging
from collections import OrderedDict
from typing import Any, Callable, List, Optional, Set
## import local files
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.Generator import Generator
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.registries.GeneratorRegistry import GeneratorRegistry
from ogd.core.models.Event import Event
from ogd.core.models.FeatureData import FeatureData
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.schemas.games.DetectorSchema import DetectorSchema
from ogd.core.schemas.games.GameSchema import GameSchema
from ogd.core.models.enums.IterationMode import IterationMode

## @class Extractor
#  Abstract base class for game feature extractors.
#  Gives a few static functions to be used across all extractor classes,
#  and defines an interface that the SessionProcessor can use.
class DetectorRegistry(GeneratorRegistry):
    """Class for registering features to listen for events.

    :return: [description]
    :rtype: [type]
    """

    # *** BUILT-INS & PROPERTIES ***

    # Base constructor for Registry.
    def __init__(self, mode:ExtractionMode, trigger_callback:Callable[[Event], None]):
        """Base constructor for Registry

        Just sets up mostly-empty dictionaries for use by the registry.
        """
        super().__init__(mode=mode)
        self._trigger_callback : Callable[[Event], None]    = trigger_callback
        self._detectors        : OrderedDict[str, Detector] = OrderedDict()

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

    def _register(self, extractor:Generator, iter_mode:IterationMode):
        if isinstance(extractor, Detector):
            _listener = GeneratorRegistry.Listener(name=extractor.Name, mode=iter_mode)
            _event_types   = extractor.EventFilter(mode=self._mode)
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

    def _getGeneratorNames(self) -> List[str]:
        """Implementation of abstract function to retrieve the names of all extractors currently registered.

        :return: A list of all currently-registered detectors.
        :rtype: List[str]
        """
        ret_val : List[str] = [feature.Name for feature in self._detectors.values()]
        return ret_val

    def _loadFromSchema(self, schema:GameSchema, loader:GeneratorLoader, overrides:Optional[List[str]]=None):
        # first, get list of what should actually be loaded.
        # TODO : move this logic as high up as possible, so that we only need to do it once for each kind of processor.
        # 1. Start with overrides, else list of enabled features in schema.
        agg_load_set : Set[DetectorSchema]
        per_load_set : Set[DetectorSchema]
        if overrides is not None:
            agg_load_set = {schema.Detectors['aggregate'][name] for name in overrides if name in schema.Detectors['aggregate'].keys()}
            per_load_set = {schema.Detectors['per_count'][name] for name in overrides if name in schema.Detectors['per_count'].keys()}
        else:
            agg_load_set = {val for val in schema.EnabledDetectors(iter_modes={IterationMode.AGGREGATE}, extract_modes={self._mode}).values() if isinstance(val, DetectorSchema)}
            per_load_set = {val for val in schema.EnabledDetectors(iter_modes={IterationMode.PERCOUNT}, extract_modes={self._mode}).values() if isinstance(val, DetectorSchema)}
        # 2. Now that we know what needs loading, load them and register.
        # TODO : right now, Detectors are at weird halfway point wrt whether they can be aggregate and percount or not. Need to resolve that.
        detector : Optional[Detector]
        for agg_schema in agg_load_set:
            detector = loader.LoadDetector(detector_type=agg_schema.TypeName, name=agg_schema.Name, schema_args=agg_schema.NonStandardElements, trigger_callback=self._trigger_callback)
            if detector is not None and self._mode in detector.AvailableModes():
                    self.Register(extractor=detector, iter_mode=IterationMode.AGGREGATE)
        for per_schema in per_load_set:
            for i in schema.GetCountRange(count=per_schema.NonStandardElements.get('count', 1)):
                instance_name = f"{per_schema.NonStandardElements.get('prefix', '')}{i}_{per_schema.Name}"
                detector = loader.LoadDetector(detector_type=per_schema.TypeName, name=per_schema.Name, schema_args=per_schema.NonStandardElements, trigger_callback=self._trigger_callback)
                if detector is not None and self._mode in detector.AvailableModes():
                        self.Register(extractor=detector, iter_mode=IterationMode.PERCOUNT)

    def _updateFromEvent(self, event:Event) -> None:
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
                    self._detectors[listener.name].UpdateFromEvent(event)
        # don't forget to send to any features listening for "all" events
        for listener in self._event_registry["all_events"]:
            if listener.name in self._detectors.keys():
                self._detectors[listener.name].UpdateFromEvent(event)

    def _updateFromFeatureData(self, feature:FeatureData) -> None:
        return

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
