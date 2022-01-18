## import standard libraries
import logging
from typing import Any, List, Type, Union
## import local files
import utils
from extractors.FeatureLoader import FeatureLoader
from extractors.PopulationExtractor import PopulationExtractor
from extractors.PlayerExtractor import PlayerExtractor
from extractors.SessionExtractor import SessionExtractor
from games.AQUALAB.AqualabLoader import AqualabLoader
from games.CRYSTAL.CrystalExtractor import CrystalExtractor
from games.JOWILDER.JowilderExtractor import JowilderExtractor
from games.LAKELAND.LakelandExtractor import LakelandExtractor
from games.MAGNET.MagnetExtractor import MagnetExtractor
from games.SHADOWSPECT.ShadowspectLoader import ShadowspectLoader
from games.WAVES.WaveLoader import WaveLoader
from managers.Request import Request
from schemas.GameSchema import GameSchema
from schemas.Event import Event

class ExtractorManager:
    def __init__(self, game_id:str, settings):
        # self._settings = settings
        self._extractor_class : Union[Type[FeatureLoader],None]  = None
        self._pop_processor   : Union[PopulationExtractor, None] = None
        self._play_processor  : Union[PlayerExtractor, None]    = None
        self._sess_processor  : Union[SessionExtractor, None]    = None
        self._prepareExtractor(game_id=game_id)

    def ProcessEvent(self, event:Event, separator:str = "\t") -> None:
        if self._pop_processor is not None:
            self._pop_processor.ProcessEvent(event=event)
        if self._sess_processor is not None:
            self._sess_processor.ProcessEvent(event=event)

    def HasExtractor(self) -> bool:
        return self._extractor_class is not None

    def GetSessionFeatureNames(self) -> List[str]:
        return self._sess_processor.GetSessionFeatureNames() if self._sess_processor is not None else []

    def GetSessionFeatures(self) -> List[List[Any]]:
        return self._sess_processor.GetSessionFeatures() if self._sess_processor is not None else []

    def GetPlayerFeatureNames(self) -> List[str]:
        return self._play_processor.GetPlayerFeatureNames() if self._play_processor is not None else []

    def GetPlayerFeatures(self) -> List[List[Any]]:
        return self._play_processor.GetPlayerFeatures() if self._play_processor is not None else []

    def GetPopulationFeatureNames(self) -> List[str]:
        return self._pop_processor.GetPopulationFeatureNames() if self._pop_processor is not None else []

    def GetPopulationFeatures(self) -> List[Any]:
        return self._pop_processor.GetPopulationFeatures() if self._pop_processor is not None else []

    def CalculateAggregateSessionFeatures(self) -> None:
        if self._sess_processor is not None:
            self._sess_processor.CalculateAggregateFeatures()

    def CalculateAggregatePlayerFeatures(self) -> None:
        if self._play_processor is not None:
            self._play_processor.CalculateAggregateFeatures()
    
    def CalculateAggregatePopulationFeatures(self) -> None:
        if self._pop_processor is not None:
            self._pop_processor.CalculateAggregateFeatures()

    def ClearSessionLines(self) -> None:
        if self._sess_processor is not None:
            self._sess_processor.ClearLines()

    def ClearPlayerLines(self) -> None:
        if self._play_processor is not None:
            self._play_processor.ClearLines()

    def ClearPopulationLines(self) -> None:
        if self._pop_processor is not None:
            self._pop_processor.ClearLines()

    def _prepareExtractor(self, game_id:str) -> None:
        game_extractor: Union[type,None] = None
        if game_id == "AQUALAB":
            game_extractor = AqualabLoader
        elif game_id == "CRYSTAL":
            game_extractor = CrystalExtractor
        elif game_id == "JOWILDER":
            game_extractor = JowilderExtractor
        elif game_id == "LAKELAND":
            game_extractor = LakelandExtractor
        elif game_id == "MAGNET":
            game_extractor = MagnetExtractor
        elif game_id == "SHADOWSPECT":
            game_extractor = ShadowspectLoader
        elif game_id == "WAVES":
            game_extractor = WaveLoader
        elif game_id in ["BACTERIA", "BALLOON", "CYCLE_CARBON", "CYCLE_NITROGEN", "CYCLE_WATER", "EARTHQUAKE", "SHIPWRECKS", "STEMPORTS", "WIND"]:
            # all games with data but no extractor.
            pass
        else:
            raise Exception(f"Got an invalid game ID ({game_id})!")
        self._extractor_class = game_extractor

    def _prepareProcessors(self, request:Request, game_schema:GameSchema, feature_overrides:Union[List[str],None]):
        if self._extractor_class is None:
            utils.Logger.toStdOut("Could not export population/session data, no game extractor given!", logging.WARN)
        else:
            if request._exports.sessions:
                self._sess_processor = SessionExtractor(ExtractorClass=self._extractor_class, game_schema=game_schema, feature_overrides=feature_overrides)
            else:
                utils.Logger.toStdOut("Session features not requested, skipping session_features file.", logging.INFO)
            if request._exports.population:
                self._pop_processor = PopulationExtractor(ExtractorClass=self._extractor_class, game_schema=game_schema, feature_overrides=feature_overrides)
            else:
                utils.Logger.toStdOut("Population features not requested, skipping population_features file.", logging.INFO)