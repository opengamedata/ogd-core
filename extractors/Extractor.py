## import standard libraries
import abc
import enum
import logging
import typing
from collections import defaultdict
from typing import Any, Dict, List, Literal, Union
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

    ## @var GameSchema _schema
    #  The schema specifying structure of data associated with an extractor.

    ## Base constructor for Extractor classes.
    #  The constructor sets an extractor's session id and range of levels,
    #  as well as initializing the features dictionary and list of played levels.
    #
    #  @param session_id  The id of the session from which we will extract features.
    #  @param game_schema A dictionary that defines how the game data itself is
    #                     structured.
    def __init__(self, session_id: str, game_schema: GameSchema):
        self._session_id  : str         = session_id
        self._game_schema : GameSchema  = game_schema
        # self._levels      : List[int]   = []
        # self._sequences   : List        = []
        self._event_registry : Dict[str,List[Extractor.Listener]]
        self._aggregates : Dict[str,Feature] = self._genAggregate()
        self._percounts  : Dict[str,List[Feature]] = self._genPerCounts()

    # string conversion for Extractors.
    def __str__(self) -> str:
        """string conversion for Extractors.

        Creates a list of all features in the extractor, separated by newlines.
        :return: A string with line-separated stringified features.
        :rtype: str
        """
        ret_val = [str(feat) for feat in self._aggregates.values()]
        for feat_list in self._percounts.values():
            ret_val += [str(feat) for feat in feat_list]
        return '\n'.join(ret_val)

    # Alternate string conversion for Extractors, with limitable number of lines.
    def to_string(self, num_lines:Union[int,None] = None) -> str:
        """Alternate string conversion for Extractors, with limitable number of lines.

        Creates a list of features in the extractor, separated by newlines.
        Optional num_lines param allows the function caller to limit number of lines in the string.
        :param num_lines: [description], defaults to None
        :type num_lines: Union[int,None], optional
        :return: A string with line-separated stringified features.
        :rtype: str
        """
        ret_val = [str(feat) for feat in self._aggregates.values()]
        for feat_list in self._percounts.values():
            ret_val += [str(feat) for feat in feat_list]
        if num_lines is None:
            return '\n'.join(ret_val)
        else:
            return '\n'.join(ret_val[:num_lines])

    @staticmethod
    def GetFeatureNames(schema:GameSchema) -> List[str]:
        ret_val : List[str] = []
        for name,aggregate in schema.aggregate_features().items():
            if aggregate.get("enabled") == True:
                ret_val.append(name)
        for name,percount in schema.percount_features().items():
            if percount.get("enabled") == True:
                if percount["count"] == "level_range":
                    count_range = Extractor._getLevelRange(schema=schema)
                else:
                    count_range = range(0,percount["count"])
                for i in count_range:
                    ret_val.append(f"{percount['prefix']}{i}_{name}")
        return ret_val

    # Static function to print column headers to a file.
    @staticmethod
    def writeCSVHeader(game_schema: GameSchema, file: typing.IO[str]) -> None:
        """Static function to print column headers to a file.

        We first create a feature dictionary, then essentially write out each key,
        with some formatting to add prefixes to features that repeat per-level
        (or repeat with a custom count).
        :param game_schema: An object that defines how the game data itself is structured
        :type game_schema: GameSchema
        :param file: An open csv file to which we will write column headers.
        :type file: typing.IO[str]
        """
        columns = Extractor.GetFeatureNames(schema=game_schema)
        file.write(",".join(columns))
        file.write("\n")

    ## Function to print data from an extractor to file.
    def writeCurrentFeatures(self, file: typing.IO[str]) -> None:
        """Function to print data from an extractor to file.

        This function should be the same across all Extractor subtypes.
        Simply prints out each value from the extractor's features dictionary.
        :param file: An open csv file to which we will write column headers.
        :type file: typing.IO[str]
        """
        column_vals = self.getCurrentFeatures()
        file.write(",".join(column_vals))
        file.write("\n")

    def getCurrentFeatures(self) -> typing.List[str]:
        #  #DO: It looks like I might be assuming that dictionaries always have same order here.
        # May need to revisit that issue. I mean, it should be fine because Python won't just go
        # and change order for no reason, but still...
        column_vals = []
        for aggregate in self._aggregates.values():
            column_vals.append(aggregate.CalculateFinalValues())
        for percounts in self._percounts.values():
            for percount in percounts:
                column_vals.append(percount.CalculateFinalValues())
        return column_vals

    def ExtractFromRow(self, event:Event, table_schema:TableSchema) -> None:
        # self.extractSequencesFromRow(event=event, table_schema=table_schema)
        self.extractFeaturesFromEvent(event=event, table_schema=table_schema)

    # def extractSequencesFromRow(self, event:Event, table_schema:TableSchema) -> None:
    #     for sequence in self._sequences:
    #         event_data = self.extractCustomSequenceEventDataFromRow(event=event, table_schema=table_schema)
    #         sequence.RegisterEvent(event.event_data, event_data=event_data)

    ## Function to custom-extract event data for a sequence.
    #  *** This function MUST BE OVERRIDDEN if you want sequence data other than the event types. ***
    #  For now, it's assumed that all sequences an extractor might want to record have a common custom-data need.
    #  At the very least, the extractor could take the union of all data its various sequences may need.
    #  In general, however, if the extractor needs multiple kinds of sequences or sequence data,
    #  it is probably better to do dedicated sequence analysis.
    # def extractCustomSequenceEventDataFromRow(self, event:Event, table_schema:TableSchema):
    #     return None

    def extractFeaturesFromEvent(self, event:Event, table_schema:TableSchema):
        """Abstract declaration of a function to perform extraction of features from a row.

        :param event: [description]
        :type event: Event
        :param table_schema: A data structure containing information on how the db
                             table assiciated with this game is structured.
        :type table_schema: TableSchema
        """
        for listener in self._event_registry[event.event_name]:
            if listener.kind == Extractor.Listener.Kinds.AGGREGATE:
                self._aggregates[listener.name].ExtractFromEvent(event)
            elif listener.kind == Extractor.Listener.Kinds.PERCOUNT:
                for percount in self._percounts[listener.name]:
                    percount.ExtractFromEvent(event)
            else:
                utils.Logger.Log(f"Got invalid listener kind {listener.kind}", logging.ERROR)

    ## Abstract declaration of a function to perform calculation of aggregate features
    #  from existing per-level/per-custom-count features.
    # @abc.abstractmethod
    def calculateAggregateFeatures(self):
        pass
    
    @abc.abstractmethod
    def _loadFeature(self, name:str, feature_args:Dict[str,Any], count_index:Union[int,None] = None) -> Feature:
        pass

    @staticmethod
    def _getLevelRange(schema:GameSchema) -> range:
        ret_val = range(0)
        if schema._min_level is not None and schema._max_level is not None:
            for i in range(schema._min_level, schema._max_level+1):
                ret_val = range(schema._min_level, schema._max_level+1)
        else:
            utils.Logger.Log(f"Could not generate per-level features, min_level={schema._min_level} and max_level={schema._max_level}", logging.ERROR)
        return ret_val

    def _genAggregate(self) -> Dict[str,Feature]:
        ret_val = {}
        for name,aggregate in self._game_schema.aggregate_features().items():
            if aggregate["enabled"] == True:
                feature = self._loadFeature(name=name, feature_args=aggregate)
                self._register(feature, Extractor.Listener.Kinds.AGGREGATE)
                ret_val[name] = feature
        return ret_val

    def _genPerCounts(self) -> Dict[str,List[Feature]]:
        ret_val = {}
        for name,percount in self._game_schema.percount_features().items():
            if percount["enabled"] == True:
                percount_instances:List[Feature] = []
                if percount["count"] == "level_range":
                    count_range = Extractor._getLevelRange(self._game_schema)
                else:
                    count_range = range(0,percount["count"])
                for i in count_range:
                    feature = self._loadFeature(name=f"{percount['prefix']}{i}_{name}", feature_args=percount, count_index=i)
                    self._register(feature, Extractor.Listener.Kinds.PERCOUNT)
                    percount_instances.append(feature)
                ret_val[name] = percount_instances
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

    ## Simple helper class to track a sequence of events, based on move types.
    # class Sequence:
    #     def __init__(self, end_function: typing.Callable[[List[Tuple]], None], end_event_type, end_event_count:int=1):
    #         self._fnEnd          = end_function
    #         self._end_event_type  = end_event_type
    #         self._end_event_count = 0               # current count of end events
    #         self._end_at_count    = end_event_count # number of end events to count before ending the sequence.
    #         self._events          = []

    #     def RegisterEvent(self, event_type, event_data) -> None:
    #         self._events.append((event_type, event_data))
    #         if event_type == self._end_event_type:
    #             self._end_event_count += 1
    #         if self._end_event_count == self._end_at_count:
    #             self._fnEnd(self._events)


