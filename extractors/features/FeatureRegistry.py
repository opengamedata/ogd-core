## import standard libraries
import enum
import json
import logging
from collections import OrderedDict
from datetime import datetime
from typing import Any, ItemsView, List, Optional
## import local files
from extractors.Extractor import Extractor
from extractors.ExtractorLoader import ExtractorLoader
from extractors.ExtractorRegistry import ExtractorRegistry
from extractors.features.Feature import Feature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
from schemas.GameSchema import GameSchema
from schemas.IterationMode import IterationMode

## @class Extractor
#  Abstract base class for game feature extractors.
#  Gives a few static functions to be used across all extractor classes,
#  and defines an interface that the SessionProcessor can use.
class FeatureRegistry(ExtractorRegistry):
    """Class for registering features to listen for events.

    :return: [description]
    :rtype: [type]
    """

    @enum.unique
    class FeatureOrders(enum.Enum):
        FIRST_ORDER = 0
        SECOND_ORDER = 1

    # *** BUILT-INS ***

    # Base constructor for Registry.
    def __init__(self, mode:ExtractionMode, order:int=len(FeatureOrders)):
        """Base constructor for Registry

        Just sets up mostly-empty dictionaries for use by the registry.
        _features is a list of feature orders, where each element is a map from feature names to actual Feature instances.
        _event_registry maps event names to Listener objects, which basically just say which feature(s) wants the given enent.
        _feature_registry maps feature names to Listener objects, which basically just say which 2nd-order feature(s) wants the given 1st-order feature.
        """
        super().__init__(mode=mode)
        self._features : List[OrderedDict[str, Feature]] = [OrderedDict() for i in range(order)]
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

    def _register(self, extractor:Extractor, mode:IterationMode):
        if isinstance(extractor, Feature):
            _listener = ExtractorRegistry.Listener(name=extractor.Name, mode=mode)
            _feature_deps = extractor.GetFeatureDependencies()
            _event_deps   = extractor.GetEventDependencies()
            # First, add feature to the _features dict.
            if len(_feature_deps) > 0:
                _feat_order = FeatureRegistry.FeatureOrders.SECOND_ORDER.value
            else:
                _feat_order = FeatureRegistry.FeatureOrders.FIRST_ORDER.value
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
            raise TypeError("FeatureRegistry was given an Extractor which was not a Feature!")

    def _getExtractorNames(self) -> List[str]:
        """Implementation of abstract function to retrieve the names of all extractors currently registered.

        :return: A list of all currently-registered features.
        :rtype: List[str]
        """
        ret_val : List[str] = []
        for order in self._features:
            for feature in order.values():
                ret_val += feature.GetFeatureNames()
        return ret_val

    def _loadFromSchema(self, schema:GameSchema, loader:ExtractorLoader, extract_mode:ExtractionMode, overrides:Optional[List[str]]):
        iter_mode = IterationMode.AGGREGATE
        for base_name,aggregate in schema.AggregateFeatures.items():
            if schema.FeatureEnabled(feature_name=base_name, iter_mode=iter_mode, extract_mode=self._mode, overrides=overrides):
                feature_type = aggregate.get('feature_type', base_name) # try to get 'feature type' from aggregate, if it's not there default to name of the config item.
                feature = loader.LoadFeature(feature_type=feature_type, name=base_name, schema_args=aggregate)
                if feature is not None and self._mode in feature.AvailableModes():
                    self.Register(extractor=feature, mode=iter_mode)
        iter_mode = IterationMode.PERCOUNT
        for base_name,percount in schema.PerCountFeatures.items():
            if schema.FeatureEnabled(feature_name=base_name, iter_mode=iter_mode, extract_mode=self._mode, overrides=overrides):
                feature_type = percount.get('feature_type', base_name) # try to get 'feature type' from percount, if it's not there default to name of the config item.
                for i in ExtractorLoader._genCountRange(count=percount["count"], schema=schema):
                    instance_name = f"{percount['prefix']}{i}_{base_name}"
                    feature = loader.LoadFeature(feature_type=feature_type, name=instance_name, schema_args=percount, count_index=i)
                    if feature is not None and self._mode in feature.AvailableModes():
                        self.Register(extractor=feature, mode=iter_mode)
        # for firstOrder in registry.FirstOrdersRequested():
        #     #TODO load firstOrder, if it's not loaded already
        #     if not firstOrder in registry.GetExtractorNames():

    def _getAggregateList(self, schema:GameSchema) -> ItemsView[str, Any]:
        return schema.AggregateFeatures.items()
    def _getPerCountList(self, schema:GameSchema) -> ItemsView[str, Any]:
        return schema.PerCountFeatures.items()

    def _extractorEnabled(self, schema:GameSchema, extractor_name:str, iter_mode:IterationMode, extract_mode:ExtractionMode, overrides:Optional[List[str]]):
        return schema.FeatureEnabled(feature_name=extractor_name, iter_mode=iter_mode, extract_mode=extract_mode, overrides=overrides)

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
                for order_key in range(len(self._features)):
                    if listener.name in self._features[order_key].keys():
                        self._features[order_key][listener.name].ExtractFromEvent(event)
        # don't forget to send to any features listening for "all" events
        for listener in self._event_registry["all_events"]:
            for order_key in range(len(self._features)):
                if listener.name in self._features[order_key].keys():
                    self._features[order_key][listener.name].ExtractFromEvent(event)

    def _extractFromFeatureData(self, feature:FeatureData) -> None:
        """Perform extraction of features from a row.

        :param event: [description]
        :type event: Event
        :param table_schema: A data structure containing information on how the db
                             table assiciated with this game is structured.
        :type table_schema: TableSchema
        """
        if feature.Name in self._feature_registry.keys():
            # send feature to every listener for the given feature name.
            for listener in self._feature_registry[feature.Name]:
                for order_key in range(len(self._features)):
                    if listener.name in self._features[order_key].keys():
                        self._features[order_key][listener.name].ExtractFromFeatureData(feature)


    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def OrderCount(self) -> int:
        """Gets the number of "orders" of features stored in the FeatureRegistry.
        For now, there's just two of them.

        :return: _description_
        :rtype: int
        """
        return len(self._features)

    def GetFeatureData(self, order:int, player_id:Optional[str]=None, sess_id:Optional[str]=None) -> List[FeatureData]:
        ret_val : List[FeatureData] = []
        for feature in self._features[order].values():
            ret_val.append(feature.ToFeatureData(player_id=player_id, sess_id=sess_id))
        return ret_val

    def GetFeatureValues(self) -> List[Any]:
        ret_val : List[Any] = []
        for order in self._features:
            for feature in order.values():
                next_vals = feature.GetFeatureValues()
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
