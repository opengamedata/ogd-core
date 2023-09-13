## import standard libraries
import logging
from typing import List, Set

# import local files
from interfaces.outerfaces.DataOuterface import DataOuterface
from schemas.Event import Event
from schemas.ExportMode import ExportMode
from schemas.FeatureData import FeatureData
from schemas.configs.GameSourceMapSchema import GameSourceSchema
from utils.Logger import Logger
from utils.utils import ExportRow

class MySQLOuterface(DataOuterface):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, game_id:str, config:GameSourceSchema, export_modes:Set[ExportMode]):
        super().__init__(game_id=game_id, export_modes=export_modes, config=config)
        # self.Open()

    def __del__(self):
        self.Close()

    # *** IMPLEMENT ABSTRACTS ***

    def _open(self) -> bool:
        return True

    def _close(self) -> bool:
        return True

    def _destination(self, mode:ExportMode) -> str:
        return "TODO"

    def _removeExportMode(self, mode:ExportMode):
        return

    def _writeRawEventsHeader(self, header:List[str]) -> None:
        return

    def _writeProcessedEventsHeader(self, header:List[str]) -> None:
        return

    def _writeSessionHeader(self, header:List[str]) -> None:
        return

    def _writePlayerHeader(self, header:List[str]) -> None:
        return

    def _writePopulationHeader(self, header:List[str]) -> None:
        return

    def _writeRawEventLines(self, events:List[Event]) -> None:
        return

    def _writeProcessedEventLines(self, events:List[Event]) -> None:
        return

    def _writeSessionLines(self, sessions:List[List[FeatureData]]) -> None:
        return

    def _writePlayerLines(self, players:List[List[FeatureData]]) -> None:
        return

    def _writePopulationLines(self, populations:List[List[FeatureData]]) -> None:
        return

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
