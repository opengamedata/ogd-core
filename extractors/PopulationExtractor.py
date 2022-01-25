# import standard libraries
import logging
import traceback
from typing import Any, Dict, IO, List, Type, Union
# import local files
import utils
from extractors.Extractor import Extractor
from extractors.FeatureLoader import FeatureLoader
from extractors.FeatureRegistry import FeatureRegistry
from extractors.PlayerExtractor import PlayerExtractor
from games.LAKELAND.LakelandLoader import LakelandLoader
from managers.Request import ExporterTypes
from schemas.Event import Event
from schemas.GameSchema import GameSchema

## @class PopulationProcessor
#  Class to extract and manage features for a processed csv file.
class PopulationExtractor(Extractor):
    ## Constructor for the PopulationProcessor class.
    #  Simply stores some data for use later, including the type of extractor to
    #  use.
    #
    #  @param ExtractorClass The type of data extractor to use for input data.
    #         This should correspond to whatever game_id is in the TableSchema.
    #  @param game_table    A data structure containing information on how the db
    #                       table assiciated with the given game is structured. 
    #  @param game_schema   A dictionary that defines how the game data itself
    #                       is structured.
    #  @param sessions_csv_file The output file, to which we'll write the processed
    #                       feature data.
    def __init__(self, LoaderClass: Type[FeatureLoader], game_schema: GameSchema,
                 feature_overrides:Union[List[str],None]=None, pop_file:Union[IO[str],None]=None):
        self._pop_file : Union[IO[str],None] = pop_file
        super().__init__(LoaderClass=LoaderClass, game_schema=game_schema, feature_overrides=feature_overrides)
        # Set up dict of sub-processors to handle each player.
        # By default, set up a "null" player, who will cover any data without a player id.
        self._player_extractors : Dict[str,PlayerExtractor] = {
            "null" : PlayerExtractor(LoaderClass=self._LoaderClass, game_schema=self._game_schema,
                                     player_id="null", feature_overrides=self._overrides)
        }

    def _prepareLoader(self) -> FeatureLoader:
        ret_val : FeatureLoader
        if self._LoaderClass is LakelandLoader:
            ret_val = LakelandLoader(player_id="population", session_id="population", game_schema=self._game_schema, feature_overrides=self._overrides, output_file=self._pop_file)
        else:
            ret_val = self._LoaderClass(player_id="population", session_id="population", game_schema=self._game_schema, feature_overrides=self._overrides)
        return ret_val

    ## Function to handle processing of a single row of data.
    #  Basically just responsible for ensuring an extractor for the session
    #  corresponding to the row already exists, then delegating the processing
    #  to that extractor.
    #  @param row_with_complex_parsed A tuple of the row data. We assume the
    #                      event_data_complex has already been parsed from JSON.
    def ProcessEvent(self, event:Event):
        # ensure we have an extractor for the given session:
        self._registry.ExtractFromEvent(event=event)
        if event.user_id is None:
            self._player_extractors["null"].ProcessEvent(event=event)
        else:
            if event.user_id not in self._player_extractors.keys():
                self._player_extractors[event.user_id] = PlayerExtractor(self._LoaderClass, game_schema=self._game_schema,
                                                                         player_id=event.user_id, feature_overrides=self._overrides)
            self._player_extractors[event.user_id].ProcessEvent(event=event)

    def PlayerCount(self):
        return len(self._player_extractors.keys()) - 1 # don't count null player

    def GetFeatureNames(self) -> List[str]:
        return self._registry.GetFeatureNames() + ["PlayerCount", "SessionCount"]
    def GetPopulationFeatureNames(self) -> List[str]:
        return self.GetPopulationFeatureNames()
    def GetPlayerFeatureNames(self) -> List[str]:
        return self._player_extractors["null"].GetFeatureNames()
    def GetSessionFeatureNames(self) -> List[str]:
        return self._player_extractors["null"].GetSessionFeatureNames()

    def GetFeatureValues(self, export_types:ExporterTypes) -> Dict[str, List[Any]]:
        ret_val = {}
        if export_types.population:
            _player_ct = self.PlayerCount()
            _sess_ct = sum([self._player_extractors[player_id].SessionCount() for player_id in self._player_extractors.keys()])
            ret_val["population"] = self._registry.GetFeatureValues() + [_player_ct, _sess_ct]
        if export_types.players or export_types.sessions:
            # first, get list of results
            _results = [player_extractor.GetFeatureValues(export_types=export_types) for player_extractor in self._player_extractors.values()]
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

    ##  Function to empty the list of lines stored by the PopulationProcessor.
    #   This is helpful if we're processing a lot of data and want to avoid
    #   eating too much memory.
    def ClearLines(self):
        utils.Logger.toStdOut(f"Clearing population entries from PopulationProcessor.", logging.DEBUG)
        self._registry = FeatureRegistry()

    def ClearPlayersLines(self):
        for player in self._player_extractors.values():
            player.ClearLines()

    def ClearSessionsLines(self):
        for player in self._player_extractors.values():
            player.ClearSessionsLines()