## import standard libraries
import abc
import enum
import logging
from os import sep, stat
import typing
from collections import defaultdict
from typing import Any, Dict, List, Union
## import local files
import utils
from extractors.Feature import Feature
from schemas.Event import Event
from schemas.GameSchema import GameSchema
from schemas.TableSchema import TableSchema

## @class Extractor
#  Abstract base class for game feature extractors.
#  Gives a few static functions to be used across all extractor classes,
#  and defines an interface that the SessionProcessor can use.
class Extractor(abc.ABC):
    class Listener:
        @enum.unique
        class Kinds(enum.Enum):
            AGGREGATE = enum.auto()
            PERCOUNT  = enum.auto()

        def __init__(self, name:str, kind:Kinds):
            self.name = name
            self.kind = kind
        
        def __str__(self) -> str:
            return f"{self.name} ({'aggregate' if self.kind == Extractor.Listener.Kinds.AGGREGATE else 'percount'})"

        def __repr__(self) -> str:
            return str(self)

    # *** ABSTRACTS ***
    
    @abc.abstractmethod
    def _loadFeature(self, feature_type:str, name:str, feature_args:Dict[str,Any], count_index:Union[int,None] = None) -> Feature:
        pass

    # *** PUBLIC BUILT-INS ***

    # Base constructor for Extractor classes.
    def __init__(self, session_id: str, game_schema: GameSchema):
        """Base constructor for Extractor classes.
        The constructor sets an extractor's session id and range of levels,
        as well as initializing the features dictionary and list of played levels.

        :param session_id: The id of the session from which we will extract features.
        :type session_id: str
        :param game_schema: A dictionary that defines how the game data itself is structured.
        :type game_schema: GameSchema
        """
        self._session_id     : str                                = session_id
        self._event_registry : Dict[str,List[Extractor.Listener]] = {}
        self._percounts      : Dict[str,Feature] = self._genPerCounts(schema=game_schema)
        self._aggregates     : Dict[str,Feature] = self._genAggregate(schema=game_schema)

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

    # Static function to print column headers to a file.
    @staticmethod
    def WriteFileHeader(game_schema: GameSchema, file: typing.IO[str], separator:str="\t") -> None:
        """Static function to print column headers to a file.

        We first create a feature dictionary, then essentially write out each key,
        with some formatting to add prefixes to features that repeat per-level
        (or repeat with a custom count).
        :param game_schema: An object that defines how the game data itself is structured
        :type game_schema: GameSchema
        :param file: An open csv file to which we will write column headers.
        :type file: typing.IO[str]
        """
        columns = Extractor._genFeatureNames(schema=game_schema)
        file.write(separator.join(columns))
        file.write("\n")

    # *** PUBLIC METHODS ***

    def ExtractFromEvent(self, event:Event) -> None:
        """Abstract declaration of a function to perform extraction of features from a row.

        :param event: [description]
        :type event: Event
        :param table_schema: A data structure containing information on how the db
                             table assiciated with this game is structured.
        :type table_schema: TableSchema
        """
        if event.event_name in self._event_registry.keys():
            for listener in self._event_registry[event.event_name]:
                if listener.kind == Extractor.Listener.Kinds.AGGREGATE:
                    self._aggregates[listener.name].ExtractFromEvent(event)
                elif listener.kind == Extractor.Listener.Kinds.PERCOUNT:
                    self._percounts[listener.name].ExtractFromEvent(event)
                else:
                    utils.Logger.Log(f"Got invalid listener kind {listener.kind}", logging.ERROR)

    ## Function to print data from an extractor to file.
    def WriteCurrentFeatures(self, file: typing.IO[str], separator:str="\t") -> None:
        """Function to print data from an extractor to file.

        This function should be the same across all Extractor subtypes.
        Simply prints out each value from the extractor's features dictionary.
        :param file: An open csv file to which we will write column headers.
        :type file: typing.IO[str]
        """
        column_vals = self.GetCurrentFeatures()
        file.write(separator.join([str(val) for val in column_vals]))
        file.write("\n")

    def GetCurrentFeatures(self) -> typing.List:
        # TODO: It looks like I might be assuming that dictionaries always have same order here.
        # May need to revisit that issue. I mean, it should be fine because Python won't just go
        # and change order for no reason, but still...
        column_vals = []
        for aggregate in self._aggregates.values():
            column_vals.append(aggregate.CalculateFinalValues())
        for percount in self._percounts.values():
            column_vals.append(percount.CalculateFinalValues())
        return column_vals

    def CalculateAggregateFeatures(self) -> None:
        """Abstract declaration of a function to perform calculation of aggregate features
        from existing per-level/per-custom-count features.
        Really just exists for compatibility with LegacyExtractors.
        """
        return

    # *** PRIVATE STATICS ***

    @staticmethod
    def _genFeatureNames(schema:GameSchema) -> List[str]:
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
        for name,aggregate in schema.aggregate_features().items():
            if aggregate.get("enabled") == True:
                ret_val.append(name)
        for name,percount in schema.percount_features().items():
            if percount.get("enabled") == True:
                for i in Extractor._genCountRange(count=percount["count"], schema=schema):
                    ret_val.append(f"{percount['prefix']}{i}_{name}")
        return ret_val

    @staticmethod
    def _genCountRange(count:Any, schema:GameSchema) -> range:
        if type(count) == str and count.lower() == "level_range":
            count_range = schema.level_range()
        else:
            count_range = range(0,int(count))
        return count_range

    # *** PRIVATE METHODS ***

    def _genAggregate(self, schema:GameSchema) -> Dict[str,Feature]:
        ret_val = {}
        for name,aggregate in schema.aggregate_features().items():
            if aggregate["enabled"] == True:
                try:
                    feature = self._loadFeature(feature_type=name, name=name, feature_args=aggregate)
                except NotImplementedError as err:
                    utils.Logger.Log(f"{name} is not a valid feature for Waves", logging.ERROR)
                else:
                    self._register(feature, Extractor.Listener.Kinds.AGGREGATE)
                    ret_val[feature.Name()] = feature
        return ret_val

    def _genPerCounts(self, schema:GameSchema) -> Dict[str,Feature]:
        ret_val = {}
        for name,percount in schema.percount_features().items():
            if percount["enabled"] == True:
                for i in Extractor._genCountRange(count=percount["count"], schema=schema):
                    try:
                        feature = self._loadFeature(feature_type=name, name=f"{percount['prefix']}{i}_{name}", feature_args=percount, count_index=i)
                    except NotImplementedError as err:
                        utils.Logger.Log(f"{name} is not a valid feature for Waves", logging.ERROR)
                    else:
                        self._register(feature=feature, kind=Extractor.Listener.Kinds.PERCOUNT)
                        ret_val[feature.Name()] = feature
        return ret_val

    def _register(self, feature:Feature, kind:Listener.Kinds):
        events = feature.GetEventTypes()
        for event in events:
            if event not in self._event_registry.keys():
                self._event_registry[event] = []
            self._event_registry[event].append(Extractor.Listener(name=feature._name, kind=kind))

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
