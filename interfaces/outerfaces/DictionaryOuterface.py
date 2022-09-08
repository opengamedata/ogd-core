## import standard libraries
import abc
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union

# import local files
from interfaces.outerfaces.DataOuterface import DataOuterface
from schemas.IDMode import IDMode
from schemas.ExportMode import ExportMode
from utils import Logger, ExportRow

class DictionaryOuterface(DataOuterface):

    # *** BUILT-INS ***

    def __init__(self, game_id:str, out_dict:Dict[str, Dict[str, Union[List[str], List[ExportRow]]]]):
        super().__init__(game_id = game_id)
        self._out = out_dict
        self._evts : List[ExportRow] = []
        self._sess : List[ExportRow] = []
        self._plrs : List[ExportRow] = []
        self._pops : List[ExportRow] = []
        self.Open()

    def __del__(self):
        self.Close()

    # *** IMPLEMENT ABSTRACTS ***

    def _open(self) -> bool:
        self._out['events']      = { "cols" : [], "vals" : self._evts }
        self._out['sessions']    = { "cols" : [], "vals" : self._sess }
        self._out['players']     = { "cols" : [], "vals" : self._plrs }
        self._out['populations'] = { "cols" : [], "vals" : self._pops }
        return True

    def _close(self) -> bool:
        return True

    def _destination(self, mode:ExportMode) -> str:
        return "RequestResult"

    def _writeEventsHeader(self, header:List[str]) -> None:
        self._out['events']['cols'] = header

    def _writeSessionHeader(self, header:List[str]) -> None:
        self._out['sessions']['cols'] = header

    def _writePlayerHeader(self, header:List[str]) -> None:
        self._out['players']['cols'] = header

    def _writePopulationHeader(self, header:List[str]) -> None:
        self._out['populations']['cols'] = header

    def _writeEventLines(self, events:List[ExportRow]) -> None:
        # I'm always a bit fuzzy on when Python will copy vs. store reference,
        # but tests indicate if we just update self._evts, self._out is updated automatically
        # since it maps to self._evts.
        # Similar for the other functions here.
        self._evts += events

    def _writeSessionLines(self, sessions:List[ExportRow]) -> None:
        self._sess += sessions

    def _writePlayerLines(self, players:List[ExportRow]) -> None:
        self._plrs += players

    def _writePopulationLines(self, populations:List[ExportRow]) -> None:
        self._pops += populations

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
