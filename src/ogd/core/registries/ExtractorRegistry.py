## import standard libraries
import enum
import json
import logging
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
## import local files
from ogd.core.generators.Generator import Generator
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.core.registries.GeneratorRegistry import GeneratorRegistry
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.schemas.games.GameSchema import GameSchema
from ogd.core.models.enums.IterationMode import IterationMode
from ogd.core.schemas.games.AggregateSchema import AggregateSchema
from ogd.core.schemas.games.PerCountSchema import PerCountSchema
from ogd.core.utils.Logger import Logger

## @class Extractor
#  Abstract base class for game feature extractors.
#  Gives a few static functions to be used across all extractor classes,
#  and defines an interface that the SessionProcessor can use.
class ExtractorRegistry(GeneratorRegistry):
    """Class for registering features to listen for events.

    :return: [description]
    :rtype: [type]
    """

    @enum.unique
    class FeatureOrders(enum.IntEnum):
        FIRST_ORDER = 0
        SECOND_ORDER = 1

        def __str__(self):
            return self.name

    # *** BUILT-INS & PROPERTIES ***

    # Base constructor for Registry.
    def __init__(self, mode:ExtractionMode, order:int=len(FeatureOrders)):
        """Base constructor for Registry

        Just sets up mostly-empty dictionaries for use by the registry.
        _features is a list of feature orders, where each element is a map from feature names to actual Feature instances.
        _event_registry maps event names to Listener objects, which basically just say which feature(s) wants the given enent.
        _feature_registry maps feature names to Listener objects, which basically just say which 2nd-order feature(s) wants the given 1st-order feature.
        """
        super().__init__(mode=mode)
        self._features : List[OrderedDict[str, Extractor]] = [OrderedDict() for i in range(order)]
        self._feature_registry: Dict[str,List[GeneratorRegistry.Listener]] = {}
        # self._features : Dict[str, OrderedDict[str, Feature]] = {
        #     "first_order" : OrderedDict(),
        #     "second_order" : OrderedDict()
        # }

    # string conversion for Extractors.
    def __str__(self) -> str:
        """string conversion for Extractors.

        Creates a list of all features in the extractor, separated by newlines.
        :return: A string with line-separated stringified features.
        :rtype: str
        """
        ret_val : List[str] = []
        for order in self._features:
            ret_val += [str(feat) for feat in order.values()]
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
        for order in self._features:
            ret_val += [str(feat) for feat in order.values()]
        if num_lines is None:
            return '\n'.join(ret_val)
        else:
            return '\n'.join(ret_val[:num_lines])

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _register(self, extractor:Generator, iter_mode:IterationMode):
        if isinstance(extractor, Extractor):
            _listener = GeneratorRegistry.Listener(name=extractor.Name, mode=iter_mode)
            _feature_deps = extractor.FeatureFilter(mode=self._mode)
            _event_deps   = extractor.EventFilter(mode=self._mode)
            # First, add feature to the _features dict.
            if len(_feature_deps) > 0:
                _feat_order = ExtractorRegistry.FeatureOrders.SECOND_ORDER.value
            else:
                _feat_order = ExtractorRegistry.FeatureOrders.FIRST_ORDER.value
            self._features[_feat_order][extractor.Name] = extractor
            # Register feature to listen for any requested first-order features.
            for _feature_dep in _feature_deps:
                if _feature_dep not in self._feature_registry.keys():
                    self._feature_registry[_feature_dep] = []
                self._feature_registry[_feature_dep].append(_listener)
            # Finally, register feature's requested events.
            if "all_events" in _event_deps:
                self._event_registry["all_events"].append(_listener)
            else:
                for event in _event_deps:
                    if event not in self._event_registry.keys():
                        self._event_registry[event] = []
                    self._event_registry[event].append(_listener)
        else:
            raise TypeError("ExtractorRegistry was given an Extractor which was not a Feature!")

    def _getGeneratorNames(self) -> List[str]:
        """Implementation of abstract function to retrieve the names of all extractors currently registered.

        :return: A list of all currently-registered features.
        :rtype: List[str]
        """
        ret_val : List[str] = []
        for order in self._features:
            for feature in order.values():
                ret_val += feature.GetFeatureNames()
        return ret_val

    def _loadFromSchema(self, schema:GameSchema, loader:GeneratorLoader, overrides:Optional[List[str]]=None):
        # first, get list of what should actually be loaded.
        # TODO : move this logic as high up as possible, so that we only need to do it once for each kind of processor.
        # 1. Start with overrides, else list of enabled features in schema.
        agg_load_set : Set[AggregateSchema]
        per_load_set : Set[PerCountSchema]
        if overrides is not None:
            agg_load_set = {schema.AggregateFeatures[name] for name in overrides if name in schema.AggregateFeatures.keys()}
            per_load_set = {schema.PerCountFeatures[name]  for name in overrides if name in schema.PerCountFeatures.keys()}
        else:
            agg_load_set = {val for val in schema.EnabledFeatures(iter_modes={IterationMode.AGGREGATE}, extract_modes={self._mode}).values() if isinstance(val, AggregateSchema)}
            per_load_set = {val for val in schema.EnabledFeatures(iter_modes={IterationMode.PERCOUNT}, extract_modes={self._mode}).values() if isinstance(val, PerCountSchema)}
        # 2. For each, grab the list of feature dependencies, and add to the list of features we want to load.
        _agg_deps = set()
        for agg in agg_load_set:
            _class = loader.GetFeatureClass(feature_type=agg.TypeName)
            if _class is not None:
                _agg_deps = _agg_deps.union(set(_class.FeatureFilter(mode=self._mode)))
        agg_load_set = agg_load_set.union({schema.AggregateFeatures[agg] for agg in _agg_deps if agg in schema.AggregateFeatures.keys()})
        _per_deps = set()
        for per in per_load_set:
            _class = loader.GetFeatureClass(feature_type=per.TypeName)
            if _class is not None:
                _per_deps = _per_deps.union(set(_class.FeatureFilter(mode=self._mode)))
        per_load_set = per_load_set.union({schema.PerCountFeatures[per] for per in _per_deps if per in schema.PerCountFeatures.keys()})
        # 3. Now that we know what needs loading, load them and register.
        for agg_schema in sorted(agg_load_set, key=lambda x : x.Name):
            feature = loader.LoadFeature(feature_type=agg_schema.TypeName, name=agg_schema.Name, schema_args=agg_schema.NonStandardElements)
            if feature is not None and self._mode in feature.AvailableModes():
                    self.Register(extractor=feature, iter_mode=IterationMode.AGGREGATE)
        for per_schema in sorted(per_load_set, key=lambda x : x.Name):
            for i in schema.GetCountRange(count=per_schema.Count):
                instance_name = f"{per_schema.Prefix}{i}_{per_schema.Name}"
                feature = loader.LoadFeature(feature_type=per_schema.TypeName, name=instance_name, schema_args=per_schema.NonStandardElements, count_index=i)
                if feature is not None and self._mode in feature.AvailableModes():
                        self.Register(extractor=feature, iter_mode=IterationMode.PERCOUNT)

    def _updateFromEvent(self, event:Event) -> None:
        """Perform extraction of features from a row.

        :param event: [description]
        :type event: Event
        :param table_schema: A data structure containing information on how the db
                             table assiciated with this game is structured.
        :type table_schema: TableSchema
        """
        listener : GeneratorRegistry.Listener = GeneratorRegistry.Listener("EMPTY", IterationMode.AGGREGATE)
        try:
            # send event to every listener for the given event name.
            for listener in self._event_registry.get(event.EventName, []):
                for order_key in range(len(self._features)):
                    if listener.name in self._features[order_key].keys():
                        self._features[order_key][listener.name].UpdateFromEvent(event)
            # don't forget to send to any features listening for "all" events
            for listener in self._event_registry["all_events"]:
                for order_key in range(len(self._features)):
                    if listener.name in self._features[order_key].keys():
                        self._features[order_key][listener.name].UpdateFromEvent(event)
        except KeyError as err:
            Logger.Log(f"{listener.name} found event {event} missing expected key: {err}", logging.ERROR)

    def _updateFromFeatureData(self, feature:FeatureData) -> None:
        """Perform extraction of features from a row.

        :param event: [description]
        :type event: Event
        :param table_schema: A data structure containing information on how the db
                             table assiciated with this game is structured.
        :type table_schema: TableSchema
        """
        listeners = self._feature_registry.get(feature.FeatureType, [])
        # send feature to every listener for the given feature name.
        for listener in listeners:
            for order_key in range(len(self._features)):
                if listener.name in self._features[order_key].keys():
                    _extractor = self._features[order_key][listener.name]
                    if feature.ExportMode in _extractor.FeatureDependencyModes():
                        self._features[order_key][listener.name].UpdateFromFeatureData(feature)


    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def OrderCount(self) -> int:
        """Gets the number of "orders" of features stored in the ExtractorRegistry.
        For now, there's just two of them.

        :return: _description_
        :rtype: int
        """
        return len(self._features)

    def GetFeatureData(self, order:int, player_id:Optional[str]=None, sess_id:Optional[str]=None) -> List[FeatureData]:
        order_index = order - 1 # orders are counted from 1, so need to adjust to index from 0.
        ret_val : List[FeatureData] = []
        for feature in self._features[order_index].values():
            ret_val.append(feature.ToFeatureData(player_id=player_id, sess_id=sess_id))
        return ret_val

    def GetFeatureValues(self) -> List[Any]:
        ret_val : List[Any] = []
        for order in self._features:
            for feature in order.values():
                next_vals = feature.GetFeatureValues()
                if len(next_vals) != len(feature.GetFeatureNames()):
                    raise ValueError(f"Feature {feature.Name} lists {len(feature.GetFeatureNames())} feature names, but returns {len(next_vals)} values!")
                ret_val += next_vals if next_vals != [] else [None]
        return ret_val

    def GetFeatureStringValues(self) -> List[str]:
        ret_val : List[str] = []
        _vals   : List[Any] = self.GetFeatureValues()

        for val in _vals:
            str_val : str
            if type(val) == dict:
                str_val = json.dumps(val)
            elif type(val) == datetime:
                str_val = val.isoformat()
            else:
                str_val = str(val)
            ret_val.append(str_val)
        return ret_val

    @property
    def FirstOrdersRequested(self) -> List[str]:
        return list(self._feature_registry.keys())

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
