## import standard libraries
import enum
import logging
from os import sep, stat
import typing
from collections import OrderedDict
from typing import Any, Dict, List, Union
## import local files
import utils
from extractors.Feature import Feature
from extractors.FeatureLoader import FeatureLoader
from schemas.Event import Event
from schemas.GameSchema import GameSchema

## @class Extractor
#  Abstract base class for game feature extractors.
#  Gives a few static functions to be used across all extractor classes,
#  and defines an interface that the SessionProcessor can use.
class FeatureRegistry:
    class Listener:
        @enum.unique
        class Kinds(enum.Enum):
            AGGREGATE = enum.auto()
            PERCOUNT  = enum.auto()

        def __init__(self, name:str, kind:Kinds):
            self.name = name
            self.kind = kind
        
        def __str__(self) -> str:
            return f"{self.name} ({'aggregate' if self.kind == FeatureRegistry.Listener.Kinds.AGGREGATE else 'percount'})"

        def __repr__(self) -> str:
            return str(self)


    # *** BUILT-INS ***

    # Base constructor for Extractor classes.
    def __init__(self, loader:FeatureLoader, game_schema:GameSchema, feature_overrides:Union[List[str],None]):
        """Base constructor for Extractor classes.
        The constructor sets an extractor's session id and range of levels,
        as well as initializing the feature
        es dictionary and list of played levels.

        :param session_id: The id of the session from which we will extract features.
        :type session_id: str
        :param game_schema: A dictionary that defines how the game data itself is structured.
        :type game_schema: GameSchema
        """
        self._overrides      : Union[List[str],None]    = feature_overrides
        self._percounts      : OrderedDict[str,Feature] = self._genPerCounts(schema=game_schema, overrides=feature_overrides)
        self._aggregates     : OrderedDict[str,Feature] = self._genAggregate(schema=game_schema, overrides=feature_overrides)
        self._loader         : FeatureLoader            = loader
        self._event_registry : Dict[str,List[FeatureRegistry.Listener]] = {"all_events":[]}

    # string conversion for Extractors.
    def __str__(self) -> str:
        """string conversion for Extractors.

        Creates a list of all features in the extractor, separated by newlines.
        :return: A string with line-separated stringified features.
        :rtype: str
        """
        ret_val  = [str(feat) for feat in self._aggregates.values()]
        ret_val += [str(feat) for feat in self._percounts.values()]
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
        ret_val  = [str(feat) for feat in self._aggregates.values()]
        ret_val += [str(feat) for feat in self._percounts.values()]
        if num_lines is None:
            return '\n'.join(ret_val)
        else:
            return '\n'.join(ret_val[:num_lines])

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def ExtractFromEvent(self, event:Event) -> None:
        """Abstract declaration of a function to perform extraction of features from a row.

        :param event: [description]
        :type event: Event
        :param table_schema: A data structure containing information on how the db
                             table assiciated with this game is structured.
        :type table_schema: TableSchema
        """
        # first, send to all listening for "all" events
        for listener in self._event_registry["all_events"]:
            if listener.kind == FeatureRegistry.Listener.Kinds.AGGREGATE:
                self._aggregates[listener.name].ExtractFromEvent(event)
            elif listener.kind == FeatureRegistry.Listener.Kinds.PERCOUNT:
                self._percounts[listener.name].ExtractFromEvent(event)
            else:
                utils.Logger.Log(f"Got invalid listener kind {listener.kind}", logging.ERROR)
        if event.event_name in self._event_registry.keys():
            for listener in self._event_registry[event.event_name]:
                if listener.kind == FeatureRegistry.Listener.Kinds.AGGREGATE:
                    self._aggregates[listener.name].ExtractFromEvent(event)
                elif listener.kind == FeatureRegistry.Listener.Kinds.PERCOUNT:
                    self._percounts[listener.name].ExtractFromEvent(event)
                else:
                    utils.Logger.Log(f"Got invalid listener kind {listener.kind}", logging.ERROR)

    def GetFeatureNames(self) -> List[str]:
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
        ret_val : List[str] = []
        for name in self._aggregates.keys():
            ret_val += self._aggregates[name].GetFeatureNames()
        for name in self._percounts.keys():
            ret_val += self._percounts[name].GetFeatureNames()
        return ret_val

    def GetFeatureValues(self) -> List[Any]:
        column_vals = []
        for name in self._aggregates.keys():
            column_vals += self._aggregates[name].GetFeatureValues()
        for name in self._percounts.keys():
            column_vals += self._percounts[name].GetFeatureValues()
        return column_vals

    # *** PRIVATE STATICS ***

    @staticmethod
    def _genCountRange(count:Any, schema:GameSchema) -> range:
        if type(count) == str and count.lower() == "level_range":
            count_range = schema.level_range()
        else:
            count_range = range(0,int(count))
        return count_range

    @staticmethod
    def _validateFeature(name:str, base_setting:bool, overrides:Union[List[str],None]):
        if overrides is not None:
            if name in overrides:
                return base_setting
            else:
                return False
        else:
            return base_setting

    # *** PRIVATE METHODS ***

    def _genAggregate(self, schema:GameSchema, overrides:Union[List[str],None]) -> 'OrderedDict[str,Feature]':
        ret_val = OrderedDict()
        for name,aggregate in schema.aggregate_features().items():
            if FeatureRegistry._validateFeature(name=name, base_setting=aggregate.get('enabled', False), overrides=overrides):
                try:
                    feature = self._loader.LoadFeature(feature_type=name, name=name, feature_args=aggregate)
                except NotImplementedError as err:
                    utils.Logger.Log(f"{name} is not a valid feature for Waves", logging.ERROR)
                else:
                    self._register(feature, FeatureRegistry.Listener.Kinds.AGGREGATE)
                    ret_val[feature.Name()] = feature
        return ret_val

    def _genPerCounts(self, schema:GameSchema, overrides:Union[List[str],None]) -> 'OrderedDict[str,Feature]':
        ret_val = OrderedDict()
        for name,percount in schema.percount_features().items():
            if FeatureRegistry._validateFeature(name=name, base_setting=percount.get('enabled', False), overrides=overrides):
                for i in FeatureRegistry._genCountRange(count=percount["count"], schema=schema):
                    try:
                        feature = self._loader.LoadFeature(feature_type=name, name=f"{percount['prefix']}{i}_{name}", feature_args=percount, count_index=i)
                    except NotImplementedError as err:
                        utils.Logger.Log(f"{name} is not a valid feature for Waves", logging.ERROR)
                    else:
                        self._register(feature=feature, kind=FeatureRegistry.Listener.Kinds.PERCOUNT)
                        ret_val[feature.Name()] = feature
        return ret_val

    def _register(self, feature:Feature, kind:Listener.Kinds):
        _listener = FeatureRegistry.Listener(name=feature._name, kind=kind)
        _event_types = feature.GetEventTypes()
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
