# import standard libraries
import logging
import traceback
from typing import Any, Dict, IO, List, Type, Union
# import local files
from utils import Logger
from extractors.Extractor import Extractor
from extractors.PlayerExtractor import PlayerExtractor
from features.FeatureData import FeatureData
from features.FeatureLoader import FeatureLoader
from features.FeatureRegistry import FeatureRegistry
from games.LAKELAND.LakelandLoader import LakelandLoader
from schemas.Event import Event
from schemas.GameSchema import GameSchema
from schemas.Request import ExporterTypes

## @class PopulationProcessor
#  Class to extract and manage features for a processed csv file.
class PopulationExtractor(Extractor):
    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _getFeatureNames(self) -> List[str]:
        return self._registry.GetFeatureNames() + ["PlayerCount", "SessionCount"]

    def _getFeatureValues(self, export_types:ExporterTypes, as_str:bool=False) -> Dict[str, List[Any]]:
        ret_val = {}
        # 1a) First, we get Population's first-order feature data:
        _player_ct = self.PlayerCount()
        _sess_ct = self.SessionCount()
        _first_order_data : Dict[str, List[FeatureData]] = self.GetFeatureData(order=FeatureRegistry.FeatureOrders.FIRST_ORDER.value)
        # 1b) Then we can side-propogate the values to second-order features, and down-propogate to other extractors:
        for feature in _first_order_data['population']:
            self.ProcessFeatureData(feature=feature)
        # 2) Second, we side-propogate feature data from players/sessions.
        for feature in _first_order_data['players']:
            self.ProcessFeatureData(feature=feature)
        for feature in _first_order_data['sessions']:
            self.ProcessFeatureData(feature=feature)
        # 3) Now, Population features have all been exposed to all first-order feature values, so we can collect all values desired for export.
        if export_types.population:
            if as_str:
                ret_val["population"] = self._registry.GetFeatureStringValues() + [str(_player_ct), str(_sess_ct)]
            else:
                ret_val["population"] = self._registry.GetFeatureValues() + [_player_ct, _sess_ct]
        # 4) Finally, all Player/Session features have been exposed to all first-order feature values, so we can collect all values desired for export.
        if export_types.players or export_types.sessions:
            # first, get list of results
            _results = [player_extractor.GetFeatureValues(export_types=export_types, as_str=as_str) for player_extractor in self._player_extractors.values()]
            # then, each result will have players or sessions or both, need to loop over and append to a list in ret_val.
            if export_types.players:
                ret_val["players"] = []
                for player in _results:
                    ret_val["players"].append(player["player"]) # here, append list of features as new line.
            if export_types.sessions:
                ret_val["sessions"] = []
                for player in _results:
                    ret_val["sessions"] += player["sessions"] # here, sessions should already be list of lists, so use +=
        return ret_val

    def _getFeatureData(self, order:int) -> Dict[str, List[FeatureData]]:
        ret_val : Dict[str, List[FeatureData]] = {}
        ret_val["population"] = self._registry.GetFeatureData(order=order)
        _result = [player_extractor.GetFeatureData(order=order) for player_extractor in self._player_extractors.values()]
        ret_val["players"] = []
        ret_val["sessions"] = []
        for player in _result:
            ret_val["players"] += player['player']
            ret_val["sessions"] += player['sessions']
        return ret_val

    ## Function to handle processing of a single row of data.
    def _processEvent(self, event:Event):
        """Function to handle processing of a single row of data.
        Basically just responsible for ensuring an extractor for the session corresponding
        to the row already exists, then delegating the processing to that extractor.

        :param event: An object with the data for the event to be processed.
        :type event: Event
        """
        # ensure we have an extractor for the given session:
        self._registry.ExtractFromEvent(event=event)
        if event.user_id is None:
            self._player_extractors["null"].ProcessEvent(event=event)
        else:
            if event.user_id not in self._player_extractors.keys():
                self._player_extractors[event.user_id] = PlayerExtractor(self._LoaderClass, game_schema=self._game_schema,
                                                                         player_id=event.user_id, feature_overrides=self._overrides)
            self._player_extractors[event.user_id].ProcessEvent(event=event)

    def _processFeatureData(self, feature: FeatureData):
        self._registry.ExtractFromFeatureData(feature=feature)
        # Down-propogate values to player (and, by extension, session) features:
        for player in self._player_extractors.values():
            player.ProcessFeatureData(feature=feature)

    def _prepareLoader(self) -> FeatureLoader:
        ret_val : FeatureLoader
        if self._LoaderClass is LakelandLoader:
            ret_val = LakelandLoader(player_id="population", session_id="population", game_schema=self._game_schema, feature_overrides=self._overrides, output_file=self._pop_file)
        else:
            ret_val = self._LoaderClass(player_id="population", session_id="population", game_schema=self._game_schema, feature_overrides=self._overrides)
        return ret_val

    # *** PUBLIC BUILT-INS ***

    ## Constructor for the PopulationProcessor class.
    def __init__(self, LoaderClass: Type[FeatureLoader], game_schema: GameSchema,
                 feature_overrides:Union[List[str],None]=None, pop_file:Union[IO[str],None]=None):
        """Constructor for the PopulationProcessor class.
        Simply stores some data for use later, including the type of extractor to use.

        :param LoaderClass: The type of data extractor to use for input data.
                            This should correspond to whatever game_id is in the TableSchema.
        :type LoaderClass: Type[FeatureLoader]
        :param game_schema: A dictionary that defines how the game data itself is structured.
        :type game_schema: GameSchema
        :param feature_overrides: _description_, defaults to None
        :type feature_overrides: Union[List[str],None], optional
        :param pop_file: _description_, defaults to None
        :type pop_file: Union[IO[str],None], optional
        """
        self._pop_file : Union[IO[str],None] = pop_file
        super().__init__(LoaderClass=LoaderClass, game_schema=game_schema, feature_overrides=feature_overrides)
        # Set up dict of sub-processors to handle each player.
        # By default, set up a "null" player, who will cover any data without a player id.
        self._player_extractors : Dict[str,PlayerExtractor] = {
            "null" : PlayerExtractor(LoaderClass=self._LoaderClass, game_schema=self._game_schema,
                                     player_id="null", feature_overrides=self._overrides)
        }

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def PlayerCount(self):
        return len(self._player_extractors.keys()) - 1 # don't count null player
    def SessionCount(self):
        sum([player.SessionCount() for player in self._player_extractors.values()])

    def GetPopulationFeatureNames(self) -> List[str]:
        return self.GetFeatureNames()
    def GetPlayerFeatureNames(self) -> List[str]:
        return self._player_extractors["null"].GetFeatureNames()
    def GetSessionFeatureNames(self) -> List[str]:
        return self._player_extractors["null"].GetSessionFeatureNames()

    ##  Function to empty the list of lines stored by the PopulationProcessor.
    #   This is helpful if we're processing a lot of data and want to avoid
    #   eating too much memory.
    def ClearLines(self):
        Logger.Log(f"Clearing features from PopulationExtractor.", logging.DEBUG, depth=2)
        self._registry = FeatureRegistry()

    def ClearPlayersLines(self):
        for player in self._player_extractors.values():
            player.ClearLines()

    def ClearSessionsLines(self):
        for player in self._player_extractors.values():
            player.ClearSessionsLines()

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***