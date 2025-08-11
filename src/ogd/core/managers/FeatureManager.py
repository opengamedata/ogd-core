## import standard libraries
import itertools
import logging
from datetime import datetime
from typing import Dict, List, Type, Optional
## import local files
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.processors.ExtractorProcessor import ExtractorProcessor
from ogd.core.processors.PopulationProcessor import PopulationProcessor
from ogd.core.processors.PlayerProcessor import PlayerProcessor
from ogd.core.processors.SessionProcessor import SessionProcessor
from ogd.core.configs.generators.GeneratorCollectionConfig import GeneratorCollectionConfig
from ogd.common.models.Event import Event
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import ExportRow

class FeatureManager:
    def __init__(self, generator_config:GeneratorCollectionConfig, LoaderClass:Optional[Type[GeneratorLoader]], feature_overrides:Optional[List[str]]):
        self._generator_configs : GeneratorCollectionConfig  = generator_config
        self._LoaderClass       : Optional[Type[GeneratorLoader]] = LoaderClass
        self._overrides         : Optional[List[str]]        = feature_overrides
        # local tracking of whether we're up-to-date on getting feature values.
        self._up_to_date        : bool                       = True
        self._latest_values     : Dict[str,List[ExportRow]]  = {}
        # local tracking of whether we used null instances in our processor hierarchies or not.
        self._used_null_play    : bool                       = False
        self._used_null_sess    : Dict[str, bool]            = { "null" : False }
        # Feature processors. We have all regardless of export modes set, so that we can support second-order features.
        # we have one population (since it's one pop per request), which has 0 or more players, and each player ID maps to a collection of 0 or more sessions.
        self._population : Optional[PopulationProcessor]                   = None
        self._players    : Optional[Dict[str, PlayerProcessor]]            = None
        self._sessions   : Optional[Dict[str, Dict[str,SessionProcessor]]] = None
        if self._LoaderClass is not None:
            self._population = PopulationProcessor(LoaderClass=self._LoaderClass, game_schema=generator_config,
                                                feature_overrides=feature_overrides)
            # need to initialize null instances for player and session processors, so at very least we can retrieve column names.
            self._players    = {
                "null" : PlayerProcessor(LoaderClass=self._LoaderClass, game_schema=self._generator_configs,
                                        player_id="null", feature_overrides=self._overrides)
            }
            self._sessions   = {
                "null" : {
                    "null" : SessionProcessor(LoaderClass=self._LoaderClass, game_schema=self._generator_configs,
                                            player_id="null", session_id="null", feature_overrides=self._overrides)
                }
            }
        else:
            Logger.Log("FeatureManager did not set up any Processors, no LoaderClass was given!", logging.WARN, depth=3)

    @property
    def FeatureLines(self) -> Dict[str, List[ExportRow]]:
        start = datetime.now()
        self._try_update()
        Logger.Log(f"Time to retrieve all feature values: {datetime.now() - start}", logging.INFO, depth=2)
        return self._latest_values

    @property
    def PopulationFeatureNames(self) -> List[str]:
        return self._population.GeneratorNames if self._population is not None else []
    @property
    def PopulationLines(self) -> List[ExportRow]:
        start = datetime.now()
        self._try_update()
        ret_val = self._latest_values.get('population', [])
        Logger.Log(f"Time to retrieve Population lines: {datetime.now() - start} to get {len(ret_val)} lines", logging.INFO, depth=2)
        return ret_val

    @property
    def PlayerFeatureNames(self) -> List[str]:
        return self._players["null"].GeneratorNames if self._players is not None else []
    @property
    def PlayerLines(self) -> List[ExportRow]:
        start   : datetime = datetime.now()
        self._try_update()
        ret_val = self._latest_values.get('players', [])
        Logger.Log(f"Time to retrieve Player lines: {datetime.now() - start} to get {len(ret_val)} lines", logging.INFO, depth=2)
        return ret_val

    @property
    def SessionFeatureNames(self) -> List[str]:
        return self._sessions["null"]["null"].GeneratorNames if self._sessions is not None else []
    def SessionLines(self, slice_num:int, slice_count:int) -> List[ExportRow]:
        start   : datetime = datetime.now()
        self._try_update()
        ret_val = self._latest_values.get('sessions', [])
        time_delta = datetime.now() - start
        Logger.Log(f"Time to retrieve Session lines for slice [{slice_num}/{slice_count}]: {time_delta} to get {len(ret_val)} lines", logging.INFO, depth=2)
        return ret_val
    
    # TODO: make this function take list of events, and do the loop over events as low in the hierarchy as possible, which technically should be faster.
    def ProcessEvent(self, event:Event) -> None:
        # 1. process at population level.
        # NOTE: removed the skipping of unrequested modes because second-order features may need feats at levels not requested for final export.
        if self._population is not None and self._players is not None and self._sessions is not None:
            self._population.ProcessEvent(event=event)
            # 2. process at player level, adding player if needed.
            _player_id = event.UserID or "null"
            if self._LoaderClass is not None and _player_id not in self._players.keys():
                self._players[_player_id] = PlayerProcessor(LoaderClass=self._LoaderClass, game_schema=self._generator_configs,
                                                            player_id=_player_id,          feature_overrides=self._overrides)
            if self._LoaderClass is not None and _player_id not in self._sessions.keys():
                self._sessions[_player_id] = {}
                self._used_null_sess[_player_id] = False

            self._players[_player_id].ProcessEvent(event=event)
            if _player_id == "null":
                self._used_null_play = True
            # 3. process at session level, adding session if needed.
            if self._LoaderClass is not None and event.SessionID not in self._sessions[_player_id].keys():
                self._sessions[_player_id][event.SessionID] = SessionProcessor(LoaderClass=self._LoaderClass, game_schema=self._generator_configs,
                                                                    player_id=_player_id,          session_id=event.SessionID,    feature_overrides=self._overrides)
            self._sessions[_player_id][event.SessionID].ProcessEvent(event=event)
            if event.SessionID == None or event.SessionID.upper() == "NULL":
                self._used_null_sess[_player_id] = True
            self._up_to_date = False

    def ProcessFeature(self) -> None:
        start = datetime.now()
        Logger.Log("Processing Feature Data...", logging.INFO, depth=3)
        # 1. Get population 1st-order data
        if self._population is not None and self._players is not None and self._sessions is not None:
            pop_data = self._population.GetFeature(order=1)
            # 2. Distribute population 1st-order data
            self._population.ProcessFeature(feature_list=pop_data)
            for player in self._players.values():
                player.ProcessFeature(feature_list=pop_data)

            for session_list in self._sessions.values():
                for session in session_list.values():
                    session.ProcessFeature(feature_list=pop_data)
            # 3. For each player, get 1st-order data
            for player_name,player in self._players.items():
                play_data = player.GetFeature(order=1)
                # 4. Distribute player 1st-order data
                self._population.ProcessFeature(feature_list=play_data)
                player.ProcessFeature(feature_list=play_data)
                for session in self._sessions.get(player_name, {}).values():
                    session.ProcessFeature(feature_list=play_data)
            # 5. For each session, get 1st-order data
            for session_list in self._sessions.values():
                for session in session_list.values():
                    sess_data = session.GetFeature(order=1)
                    # 6. Distribute session 1st-order data
                    self._population.ProcessFeature(feature_list=sess_data)
                    player = self._players.get(session._playerID, None)
                    if player is not None:
                        player.ProcessFeature(feature_list=sess_data)
                    session.ProcessFeature(feature_list=sess_data)
            Logger.Log(f"Time to process Feature Data: {datetime.now() - start}", logging.INFO, depth=3)
        else:
            Logger.Log("Skipped processing of Feature, no feature Processors available!", logging.INFO, depth=3)

    #new
    # def GetPopulationFeature(self) -> List[Feature]:
    #     if self._population is not None:
    #         population_data = self._population.GetFeature(order=1)
    #     return population_data if self._population is not None else []
    
    # def GetSessionFeature(self) -> List[Feature]:
    #     session_data=[]
    #     if self._sessions is not None:
    #         for sess_list in self._sessions.values():
    #             for session in sess_list.values():
    #                  session_data += session.GetFeature(order=1)
    #     return session_data
    

    def ClearPopulationLines(self) -> None:
        if self._population is not None:
            self._population.ClearLines()
    def ClearPlayerLines(self) -> None:
        if self._players is not None and self._LoaderClass is not None:
            for player in self._players.values():
                player.ClearLines()
            self._players = {}
            self._players["null"] = PlayerProcessor(LoaderClass=self._LoaderClass, game_schema=self._generator_configs,
                                                    player_id="null", feature_overrides=self._overrides)
    def ClearSessionLines(self) -> None:
        if self._sessions is not None and self._LoaderClass is not None:
            for sess_list in self._sessions.values():
                for sess in sess_list.values():
                    sess.ClearLines()
            self._sessions = {}
            self._sessions["null"] = {
                "null" : SessionProcessor(LoaderClass=self._LoaderClass, game_schema=self._generator_configs,
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

    def _try_update(self):
        if not self._up_to_date:
            self.ProcessFeature()
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
