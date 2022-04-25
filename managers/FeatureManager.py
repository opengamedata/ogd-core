## import standard libraries
import logging
from datetime import datetime
from typing import Any, Dict, List, Type, Union
## import local files
from utils import Logger
from extractors.ExtractorLoader import ExtractorLoader
from processors.PopulationProcessor import PopulationProcessor
from processors.PlayerProcessor import PlayerProcessor
from processors.SessionProcessor import SessionProcessor
from games.AQUALAB.AqualabLoader import AqualabLoader
from games.CRYSTAL.CrystalLoader import CrystalLoader
from games.JOWILDER.JowilderLoader import JowilderLoader
from games.LAKELAND.LakelandLoader import LakelandLoader
from games.MAGNET.MagnetLoader import MagnetLoader
from games.SHADOWSPECT.ShadowspectLoader import ShadowspectLoader
from games.SHIPWRECKS.ShipwrecksLoader import ShipwrecksLoader
from games.WAVES.WaveLoader import WaveLoader
from schemas.GameSchema import GameSchema
from schemas.Event import Event
from schemas.Request import ExporterTypes

class FeatureManager:
    def __init__(self, game_id:str, exp_types:ExporterTypes, game_schema:GameSchema, feature_overrides:Union[List[str],None]):
        self._exp_types        : ExporterTypes       = exp_types
        self._latest_results   : Dict[str,List[Any]] = {}
        self._up_to_date       : bool                = True
        self._LoaderClass      : Union[Type[ExtractorLoader],None]
        self._pop_extractor    : Union[PopulationProcessor, None] = None
        self._player_extractor : Union[PlayerProcessor, None]     = None
        self._sess_extractor   : Union[SessionProcessor, None]    = None

        self._LoaderClass   = self._prepareLoaderClass(game_id=game_id)
        if self._LoaderClass is not None:
            if exp_types.population:
                self._pop_extractor = PopulationProcessor(LoaderClass=self._LoaderClass, game_schema=game_schema,
                                                          feature_overrides=feature_overrides)
            # TODO: see if there's a good way to get actual player/session id values here.
            elif exp_types.players:
                self._player_extractor = PlayerProcessor(LoaderClass=self._LoaderClass, game_schema=game_schema,
                                                         player_id="Player", feature_overrides=feature_overrides)
            elif exp_types.sessions:
                self._sess_extractor = SessionProcessor(LoaderClass=self._LoaderClass, game_schema=game_schema,
                                                         player_id="Player", session_id="Session", feature_overrides=feature_overrides)
        else:
            Logger.Log("Could not export population/session data, no feature loader given!", logging.WARNING, depth=1)

    def ProcessEvent(self, event:Event) -> None:
        if self._pop_extractor is not None:
            self._pop_extractor.ProcessEvent(event=event)
        elif self._player_extractor is not None:
            self._player_extractor.ProcessEvent(event=event)
        elif self._sess_extractor is not None:
            self._sess_extractor.ProcessEvent(event=event)
        self._up_to_date = False

    def HasLoader(self) -> bool:
        return self._LoaderClass is not None

    def _try_update(self, as_str:bool = False):
        if not self._up_to_date:
            if self._pop_extractor is not None:
                self._latest_results = self._pop_extractor.GetFeatureValues(export_types=self._exp_types, as_str=as_str)
            elif self._player_extractor is not None:
                self._latest_results = self._player_extractor.GetFeatureValues(export_types=self._exp_types, as_str=as_str)
            elif self._sess_extractor is not None:
                self._latest_results = self._sess_extractor.GetFeatureValues(export_types=self._exp_types, as_str=as_str)
            self._up_to_date = True

    def GetFeatureValues(self, as_str:bool = False):
        self._try_update(as_str=as_str)
        return self._latest_results

    def GetPopulationFeatureNames(self) -> List[str]:
        return self._pop_extractor.GetExtractorNames() if self._pop_extractor is not None else []
    def GetPopulationFeatures(self, as_str:bool = False) -> List[Any]:
        start   : datetime = datetime.now()
        self._try_update(as_str=as_str)
        ret_val = self._latest_results.get('population', [])
        time_delta = datetime.now() - start
        Logger.Log(f"Time to retrieve Population lines: {time_delta} to get {len(ret_val)} lines", logging.INFO, depth=2)
        return ret_val

    def GetPlayerFeatureNames(self) -> List[str]:
        if self._pop_extractor is not None:
            return self._pop_extractor.GetPlayerFeatureNames()
        elif self._player_extractor is not None:
            return self._player_extractor.GetExtractorNames()
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
        if self._pop_extractor is not None:
            return self._pop_extractor.GetSessionFeatureNames()
        elif self._player_extractor is not None:
            return self._player_extractor.GetSessionFeatureNames()
        elif self._sess_extractor is not None:
            return self._sess_extractor.GetExtractorNames()
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
        if self._pop_extractor is not None:
            self._pop_extractor.ClearLines()

    def ClearPlayerLines(self) -> None:
        if self._pop_extractor is not None:
            self._pop_extractor.ClearPlayersLines()
        elif self._player_extractor is not None:
            self._player_extractor.ClearLines()

    def ClearSessionLines(self) -> None:
        if self._pop_extractor is not None:
            self._pop_extractor.ClearSessionsLines()
        elif self._player_extractor is not None:
            self._player_extractor.ClearSessionsLines()
        elif self._sess_extractor is not None:
            self._sess_extractor.ClearLines()

    def _prepareLoaderClass(self, game_id:str) -> Union[Type[ExtractorLoader],None]:
        _loader_class: Union[Type[ExtractorLoader],None] = None
        if game_id == "AQUALAB":
            _loader_class = AqualabLoader
        elif game_id == "CRYSTAL":
            _loader_class = CrystalLoader
        elif game_id == "JOWILDER":
            _loader_class = JowilderLoader
        elif game_id == "LAKELAND":
            _loader_class = LakelandLoader
        elif game_id == "MAGNET":
            _loader_class = MagnetLoader
        elif game_id == "SHADOWSPECT":
            _loader_class = ShadowspectLoader
        elif game_id == "SHIPWRECKS":
            _loader_class = ShipwrecksLoader
        elif game_id == "WAVES":
            _loader_class = WaveLoader
        elif game_id in ["BACTERIA", "BALLOON", "CYCLE_CARBON", "CYCLE_NITROGEN", "CYCLE_WATER", "EARTHQUAKE", "STEMPORTS", "WIND"]:
            # all games with data but no extractor.
            pass
        else:
            raise Exception(f"Got an invalid game ID ({game_id})!")
        return _loader_class
