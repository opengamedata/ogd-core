## import standard libraries
import logging
from datetime import datetime
from typing import Any, Dict, List, Type, Optional
## import local files
from utils import Logger
from extractors.ExtractorLoader import ExtractorLoader
from processors.PopulationProcessor import PopulationProcessor
from processors.PlayerProcessor import PlayerProcessor
from processors.SessionProcessor import SessionProcessor
from schemas.GameSchema import GameSchema
from schemas.Event import Event
from schemas.Request import ExporterTypes

class FeatureManager:
    def __init__(self, LoaderClass:Type[ExtractorLoader], exp_types:ExporterTypes, game_schema:GameSchema, feature_overrides:Optional[List[str]]):
        self._exp_types        : ExporterTypes       = exp_types
        self._latest_results   : Dict[str,List[Any]] = {}
        self._up_to_date       : bool                = True
        self._pop_processor    : Optional[PopulationProcessor]  = None
        self._player_processor : Optional[PlayerProcessor]      = None
        self._sess_processor   : Optional[SessionProcessor]     = None
        self._LoaderClass      : Optional[Type[ExtractorLoader]] = LoaderClass

        if self._LoaderClass is not None:
            if exp_types.population:
                self._pop_processor = PopulationProcessor(LoaderClass=self._LoaderClass, game_schema=game_schema,
                                                          feature_overrides=feature_overrides)
            elif exp_types.players:
                self._player_processor = PlayerProcessor(LoaderClass=self._LoaderClass, game_schema=game_schema,
                                                         player_id="Player", feature_overrides=feature_overrides)
            elif exp_types.sessions:
                self._sess_processor = SessionProcessor(LoaderClass=self._LoaderClass, game_schema=game_schema,
                                                         player_id="Player", session_id="Session", feature_overrides=feature_overrides)
        else:
            Logger.Log("Could not export population/session data, no feature loader given!", logging.WARNING, depth=1)

    def ProcessEvent(self, event:Event) -> None:
        if self._pop_processor is not None:
            self._pop_processor.ProcessEvent(event=event)
        elif self._player_processor is not None:
            self._player_processor.ProcessEvent(event=event)
        elif self._sess_processor is not None:
            self._sess_processor.ProcessEvent(event=event)
        self._up_to_date = False

    def HasLoader(self) -> bool:
        return self._LoaderClass is not None

    def GetFeatureValues(self, as_str:bool = False) -> Dict[str, List[Any]]:
        self._try_update(as_str=as_str)
        return self._latest_results

    def GetPopulationFeatureNames(self) -> List[str]:
        return self._pop_processor.GetExtractorNames() if self._pop_processor is not None else []
    def GetPopulationFeatures(self, as_str:bool = False) -> List[Any]:
        start   : datetime = datetime.now()
        self._try_update(as_str=as_str)
        ret_val = self._latest_results.get('population', [])
        time_delta = datetime.now() - start
        Logger.Log(f"Time to retrieve Population lines: {time_delta} to get {len(ret_val)} lines", logging.INFO, depth=2)
        return ret_val

    def GetPlayerFeatureNames(self) -> List[str]:
        if self._pop_processor is not None:
            return self._pop_processor.GetPlayerFeatureNames()
        elif self._player_processor is not None:
            return self._player_processor.GetExtractorNames()
        else:
            return []
    def GetPlayerFeatures(self, slice_num:int, slice_count:int, as_str:bool = False) -> List[List[Any]]:
        start   : datetime = datetime.now()
        self._try_update(as_str=as_str)
        ret_val = self._latest_results.get('players', [])
        time_delta = datetime.now() - start
        Logger.Log(f"Time to retrieve Player lines for slice [{slice_num}/{slice_count}]: {time_delta} to get {len(ret_val)} lines", logging.INFO, depth=2)
        return ret_val

    def GetSessionFeatureNames(self) -> List[str]:
        if self._pop_processor is not None:
            return self._pop_processor.GetSessionFeatureNames()
        elif self._player_processor is not None:
            return self._player_processor.GetSessionFeatureNames()
        elif self._sess_processor is not None:
            return self._sess_processor.GetExtractorNames()
        else:
            return []
    def GetSessionFeatures(self, slice_num:int, slice_count:int, as_str:bool = False) -> List[List[Any]]:
        start   : datetime = datetime.now()
        self._try_update(as_str=as_str)
        ret_val = self._latest_results.get('sessions', [])
        time_delta = datetime.now() - start
        Logger.Log(f"Time to retrieve Session lines for slice [{slice_num}/{slice_count}]: {time_delta} to get {len(ret_val)} lines", logging.INFO, depth=2)
        return ret_val

    def ClearPopulationLines(self) -> None:
        if self._pop_processor is not None:
            self._pop_processor.ClearLines()
    def ClearPlayerLines(self) -> None:
        if self._pop_processor is not None:
            self._pop_processor.ClearPlayersLines()
        elif self._player_processor is not None:
            self._player_processor.ClearLines()
    def ClearSessionLines(self) -> None:
        if self._pop_processor is not None:
            self._pop_processor.ClearSessionsLines()
        elif self._player_processor is not None:
            self._player_processor.ClearSessionsLines()
        elif self._sess_processor is not None:
            self._sess_processor.ClearLines()

    def _try_update(self, as_str:bool = False):
        if not self._up_to_date:
            if self._pop_processor is not None:
                self._latest_results = self._pop_processor.GetFeatureValues(export_types=self._exp_types, as_str=as_str)
            elif self._player_processor is not None:
                self._latest_results = self._player_processor.GetFeatureValues(export_types=self._exp_types, as_str=as_str)
            elif self._sess_processor is not None:
                self._latest_results = self._sess_processor.GetFeatureValues(export_types=self._exp_types, as_str=as_str)
            self._up_to_date = True
