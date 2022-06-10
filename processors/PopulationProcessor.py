# import standard libraries
import logging
import traceback
from typing import Any, Dict, IO, List, Type, Optional
# import local files
from extractors.ExtractorRegistry import ExtractorRegistry
from schemas.FeatureData import FeatureData
from extractors.ExtractorLoader import ExtractorLoader
from extractors.features.FeatureRegistry import FeatureRegistry
from processors.FeatureProcessor import FeatureProcessor
from processors.PlayerProcessor import PlayerProcessor
from schemas.Event import Event
from schemas.GameSchema import GameSchema
from requests.Request import ExporterTypes
from utils import Logger

## @class PopulationProcessor
#  Class to extract and manage features for a processed csv file.
class PopulationProcessor(FeatureProcessor):
    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _prepareLoader(self) -> ExtractorLoader:
        return self._LoaderClass(player_id="population",        session_id="population",
                                 game_schema=self._game_schema, feature_overrides=self._overrides)

    def _getExtractorNames(self) -> List[str]:
        if isinstance(self._registry, FeatureRegistry):
            return self._registry.GetExtractorNames() + ["PlayerCount", "SessionCount"]
        else:
            raise TypeError("PopulationProcessor's registry is not a FeatureRegistry!")

    ## Function to handle processing of a single row of data.
    def _processEvent(self, event:Event):
        """Function to handle processing of a single row of data.
        Basically just responsible for ensuring an extractor for the session corresponding
        to the row already exists, then delegating the processing to that extractor.

        :param event: An object with the data for the event to be processed.
        :type event: Event
        """
        # ensure we have an extractor for the given session:
        if self._registry is not None:
            self._registry.ExtractFromEvent(event=event)
            if event.UserID is None:
                self._player_processors["null"].ProcessEvent(event=event)
            else:
                if event.UserID not in self._player_processors.keys():
                    self._player_processors[event.UserID] = PlayerProcessor(self._LoaderClass, game_schema=self._game_schema,
                                                                            player_id=event.UserID, feature_overrides=self._overrides)
                self._player_processors[event.UserID].ProcessEvent(event=event)

    def _processFeatureData(self, feature: FeatureData):
        if self._registry is not None:
            self._registry.ExtractFromFeatureData(feature=feature)
            # Down-propogate values to player (and, by extension, session) features:
            for player in self._player_processors.values():
                player.ProcessFeatureData(feature=feature)

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
        if export_types.population and isinstance(self._registry, FeatureRegistry):
            if as_str:
                ret_val["population"] = self._registry.GetFeatureStringValues() + [str(_player_ct), str(_sess_ct)]
            else:
                ret_val["population"] = self._registry.GetFeatureValues() + [_player_ct, _sess_ct]
        # 4) Finally, all Player/Session features have been exposed to all first-order feature values, so we can collect all values desired for export.
        if export_types.players or export_types.sessions:
            # first, get list of results
            _results = [player_extractor.GetFeatureValues(export_types=export_types, as_str=as_str) for player_extractor in self._player_processors.values()]
            # then, each result will have players or sessions or both, need to loop over and append to a list in ret_val.
            if export_types.players:
                ret_val["players"] = []
                for player in _results:
                    ret_val["players"].append(player["players"]) # here, append list of features as new line.
            if export_types.sessions:
                ret_val["sessions"] = []
                for player in _results:
                    ret_val["sessions"] += player["sessions"] # here, sessions should already be list of lists, so use +=
        return ret_val

    def _getFeatureData(self, order:int) -> Dict[str, List[FeatureData]]:
        ret_val : Dict[str, List[FeatureData]] = { "population":[] }
        if self._registry is not None:
            ret_val["population"] = self._registry.GetFeatureData(order=order)
        _result = [player_extractor.GetFeatureData(order=order) for player_extractor in self._player_processors.values()]
        ret_val["players"] = []
        ret_val["sessions"] = []
        for player in _result:
            ret_val["players"] += player['players']
            ret_val["sessions"] += player['sessions']
        return ret_val

    ##  Function to empty the list of lines stored by the PopulationProcessor.
    #   This is helpful if we're processing a lot of data and want to avoid
    #   eating too much memory.
    def _clearLines(self) -> None:
        Logger.Log(f"Clearing features from PopulationProcessor.", logging.DEBUG, depth=2)
        self._registry = FeatureRegistry()

    # *** BUILT-INS ***

    ## Constructor for the PopulationProcessor class.
    def __init__(self, LoaderClass: Type[ExtractorLoader], game_schema: GameSchema,
                 feature_overrides:Optional[List[str]]=None):
        """Constructor for the PopulationProcessor class.
        Simply stores some data for use later, including the type of extractor to use.

        :param LoaderClass: The type of data extractor to use for input data.
                            This should correspond to whatever game_id is in the TableSchema.
        :type LoaderClass: Type[ExtractorLoader]
        :param game_schema: A dictionary that defines how the game data itself is structured.
        :type game_schema: GameSchema
        :param feature_overrides: _description_, defaults to None
        :type feature_overrides: Optional[List[str]], optional
        :param pop_file: _description_, defaults to None
        :type pop_file: Optional[IO[str]], optional
        """
        super().__init__(LoaderClass=LoaderClass, game_schema=game_schema, feature_overrides=feature_overrides)
        # Set up dict of sub-processors to handle each player.
        # By default, set up a "null" player, who will cover any data without a player id.
        self._player_processors : Dict[str,PlayerProcessor] = {
            "null" : PlayerProcessor(LoaderClass=self._LoaderClass, game_schema=self._game_schema,
                                     player_id="null", feature_overrides=self._overrides)
        }

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def PlayerCount(self):
        return len(self._player_processors.keys()) - 1 # don't count null player
    def SessionCount(self):
        return sum([player.SessionCount() for player in self._player_processors.values()])

    def GetPlayerFeatureNames(self) -> List[str]:
        return self._player_processors["null"].GetExtractorNames()
    def GetSessionFeatureNames(self) -> List[str]:
        return self._player_processors["null"].GetSessionFeatureNames()

    def ClearPlayersLines(self):
        for player in self._player_processors.values():
            player.ClearLines()
    def ClearSessionsLines(self):
        for player in self._player_processors.values():
            player.ClearSessionsLines()

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***