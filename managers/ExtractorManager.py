## import standard libraries
import logging
from typing import Any, Dict, List, Type, Union
## import local files
from utils import Logger
from features.FeatureLoader import FeatureLoader
from extractors.PopulationExtractor import PopulationExtractor
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

class ExtractorManager:
    def __init__(self, game_id:str, exp_types:ExporterTypes, game_schema:GameSchema, feature_overrides:Union[List[str],None]):
        self._exp_types      : ExporterTypes       = exp_types
        self._latest_results : Dict[str,List[Any]] = {}
        self._up_to_date     : bool                = True
        self._LoaderClass    : Union[Type[FeatureLoader],None]
        self._pop_extractor  : Union[PopulationExtractor, None]

        self._LoaderClass   = self._prepareLoaderClass(game_id=game_id)
        if self._LoaderClass is not None:
            if exp_types.population:
                self._pop_extractor = PopulationExtractor(LoaderClass=self._LoaderClass, game_schema=game_schema, feature_overrides=feature_overrides)
        else:
            Logger.Log("Could not export population/session data, no game extractor given!", logging.WARN)

    def ProcessEvent(self, event:Event) -> None:
        if self._pop_extractor is not None:
            self._pop_extractor.ProcessEvent(event=event)
        self._up_to_date = False

    def HasLoader(self) -> bool:
        return self._LoaderClass is not None

    def _try_update(self, as_str:bool = False):
        if not self._up_to_date:
            if self._pop_extractor is not None:
                self._latest_results = self._pop_extractor.GetFeatureValues(export_types=self._exp_types, as_str=as_str)
            self._up_to_date = True

    def GetFeatureValues(self, as_str:bool = False):
        self._try_update(as_str=as_str)
        return self._latest_results

    def GetPopulationFeatureNames(self) -> List[str]:
        return self._pop_extractor.GetPopulationFeatureNames() if self._pop_extractor is not None else []
    def GetPopulationFeatures(self, as_str:bool = False) -> List[Any]:
        self._try_update(as_str=as_str)
        return self._latest_results.get('population', [])

    def GetPlayerFeatureNames(self) -> List[str]:
        return self._pop_extractor.GetPlayerFeatureNames() if self._pop_extractor is not None else []
    def GetPlayerFeatures(self, as_str:bool = False) -> List[List[Any]]:
        self._try_update(as_str=as_str)
        return self._latest_results.get('players', [])

    def GetSessionFeatureNames(self) -> List[str]:
        return self._pop_extractor.GetSessionFeatureNames() if self._pop_extractor is not None else []
    def GetSessionFeatures(self, as_str:bool = False) -> List[List[Any]]:
        self._try_update(as_str=as_str)
        return self._latest_results.get('sessions', [])

    def ClearPopulationLines(self) -> None:
        if self._pop_extractor is not None:
            self._pop_extractor.ClearLines()

    def ClearPlayerLines(self) -> None:
        if self._pop_extractor is not None:
            self._pop_extractor.ClearPlayersLines()

    def ClearSessionLines(self) -> None:
        if self._pop_extractor is not None:
            self._pop_extractor.ClearSessionsLines()

    def _prepareLoaderClass(self, game_id:str) -> Union[Type[FeatureLoader],None]:
        _loader_class: Union[Type[FeatureLoader],None] = None
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