## import standard libraries
import itertools
import logging
from datetime import datetime
from typing import Dict, List, Type, Optional, Set, Tuple, Union
## import local files
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.generators.models.Model import Model
from ogd.core.processors.ExtractorProcessor import ExtractorProcessor
from ogd.common.schemas.games.GameSchema import GameSchema
from ogd.common.models.FeatureData import FeatureData
from ogd.common.models.Event import Event
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import ExportRow

class ModelManager:
    def __init__(self, game_schema:GameSchema, LoaderClass:Optional[Type[GeneratorLoader]], feature_overrides:Optional[List[str]]):
        self._game_schema    : GameSchema                 = game_schema
        self._LoaderClass    : Optional[Type[GeneratorLoader]] = LoaderClass
        self._overrides      : Optional[List[str]]        = feature_overrides
        # local tracking of whether we're up-to-date on getting feature values.
        self._up_to_date     : bool                       = True
        self._latest_values  : Dict[str,List[ExportRow]]  = {}
        self._models         : ModelProcessor
        if self._LoaderClass is not None:
            self._models = ModelProcessor(LoaderClass=self._LoaderClass, game_schema=game_schema,
                                                feature_overrides=feature_overrides)
        else:
            Logger.Log(f"ModelManager did not set up any Processors, no LoaderClass was given!", logging.WARN, depth=3)

    # TODO: make this function take list of events, and do the loop over events as low in the hierarchy as possible, which technically should be faster.
    def ProcessEvent(self, event:Event) -> None:
        # 1. process at population level.
        # NOTE: removed the skipping of unrequested modes because second-order features may need feats at levels not requested for final export.
        if self._models is not None:
            self._models.ProcessEvent(event=event)
            self._up_to_date = False

    def ProcessFeatureData(self, feature:FeatureData) -> None:
        start = datetime.now()
        Logger.Log(f"Processing Feature Data for Modeling...", logging.INFO, depth=3)
        # 1. Get population 1st-order data
        if self._models is not None:
            # 2. Distribute population 1st-order data
            self._models.ProcessFeatureData(feature=feature)
            Logger.Log(f"Time for modeling to process Feature Data: {datetime.now() - start}", logging.INFO, depth=3)
        else:
            Logger.Log(f"Skipped model processing of FeatureData, no model Processors available!", logging.INFO, depth=3)

    def GetModels(self, as_str:bool = False) -> Dict[str, Model]:
        start = datetime.now()
        self._try_update(as_str=as_str)
        Logger.Log(f"Time to retrieve all feature values: {datetime.now() - start}", logging.INFO, depth=2)
        return self._latest_values

    def GetPopulationFeatureNames(self) -> List[str]:
        return self._population.GeneratorNames if self._population is not None else []
    def GetPopulationFeatures(self, as_str:bool = False) -> List[ExportRow]:
        start = datetime.now()
        self._try_update(as_str=as_str)
        ret_val = self._latest_values.get('population', [])
        Logger.Log(f"Time to retrieve Population lines: {datetime.now() - start} to get {len(ret_val)} lines", logging.INFO, depth=2)
        return ret_val

    def GetPlayerFeatureNames(self) -> List[str]:
        return self._players["null"].GeneratorNames if self._players is not None else []
    def GetPlayerFeatures(self, as_str:bool = False) -> List[ExportRow]:
        start   : datetime = datetime.now()
        self._try_update(as_str=as_str)
        ret_val = self._latest_values.get('players', [])
        Logger.Log(f"Time to retrieve Player lines: {datetime.now() - start} to get {len(ret_val)} lines", logging.INFO, depth=2)
        return ret_val

    def GetSessionFeatureNames(self) -> List[str]:
        return self._sessions["null"]["null"].GeneratorNames if self._sessions is not None else []
    def GetSessionFeatures(self, slice_num:int, slice_count:int, as_str:bool = False) -> List[ExportRow]:
        start   : datetime = datetime.now()
        self._try_update(as_str=as_str)
        ret_val = self._latest_values.get('sessions', [])
        time_delta = datetime.now() - start
        Logger.Log(f"Time to retrieve Session lines for slice [{slice_num}/{slice_count}]: {time_delta} to get {len(ret_val)} lines", logging.INFO, depth=2)
        return ret_val

    def ClearPopulationLines(self) -> None:
        if self._population is not None:
            self._population.ClearLines()
    def ClearPlayerLines(self) -> None:
        if self._players is not None and self._LoaderClass is not None:
            for player in self._players.values():
                player.ClearLines()
            self._players = {}
            self._players["null"] = PlayerProcessor(LoaderClass=self._LoaderClass, game_schema=self._game_schema,
                                                    player_id="null", feature_overrides=self._overrides)
    def ClearSessionLines(self) -> None:
        if self._sessions is not None and self._LoaderClass is not None:
            for sess_list in self._sessions.values():
                for sess in sess_list.values():
                    sess.ClearLines()
            self._sessions = {}
            self._sessions["null"] = {
                "null" : SessionProcessor(LoaderClass=self._LoaderClass, game_schema=self._game_schema,
                                        player_id="null", session_id="null", feature_overrides=self._overrides)
            }

    def _flatHierarchy(self) -> List[ExtractorProcessor]:
        ret_val : List[ExtractorProcessor] = []
        if self._population is not None:
            ret_val = [self._population]
        if self._players is not None:
            ret_val += self._players.values()
        if self._sessions is not None:
            for sess_list in self._sessions.values():
                ret_val += sess_list.values()
        return ret_val

    def _try_update(self, as_str:bool = False):
        if not self._up_to_date:
            self.ProcessFeatureData()
            # for some reason, this didn't work as sum over list of lists, so get sessions manually with a normal loop:
            list_o_playlists : List[List[ExportRow]]       = [player.Lines for player_id,player in self._players.items() if (player_id != "null" or self._used_null_play)] if self._players is not None else []
            flat_playlist    : List[ExportRow]             = list(itertools.chain.from_iterable(list_o_playlists))
            list_o_sesslists : List[List[List[ExportRow]]] = [[session.Lines for session_id,session in session_list.items() if (session_id != "null" or self._used_null_sess[player_name])] for player_name,session_list in self._sessions.items()] if self._sessions is not None else []
            flat_sesslist    : List[ExportRow]             = list(itertools.chain.from_iterable(itertools.chain.from_iterable(list_o_sesslists)))
            self._latest_values = {
                "population" : self._population.Lines if self._population is not None else [],
                "players"    : flat_playlist,
                "sessions"   : flat_sesslist
            }
            self._up_to_date = True
