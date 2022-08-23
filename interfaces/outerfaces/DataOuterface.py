## import standard libraries
import abc
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union

# import local files
from interfaces.Interface import Interface
from schemas.IDMode import IDMode
from schemas.ExtractionMode import ExtractionMode
from utils import Logger, ExportRow

class DataOuterface(Interface):

    # *** ABSTRACTS ***

    @abc.abstractmethod
    def _destination(self, mode:ExtractionMode) -> str:
        pass

    @abc.abstractmethod
    def _writeEventsHeader(self, header:List[str]) -> None:
        pass

    @abc.abstractmethod
    def _writeSessionHeader(self, header:List[str]) -> None:
        pass

    @abc.abstractmethod
    def _writePlayerHeader(self, header:List[str]) -> None:
        pass

    @abc.abstractmethod
    def _writePopulationHeader(self, header:List[str]) -> None:
        pass

    @abc.abstractmethod
    def _writeEventLines(self, events:List[str]) -> None:
        pass

    @abc.abstractmethod
    def _writeSessionLines(self, sessions:List[ExportRow]) -> None:
        pass

    @abc.abstractmethod
    def _writePlayerLines(self, players:List[ExportRow]) -> None:
        pass

    @abc.abstractmethod
    def _writePopulationLines(self, populations:List[ExportRow]) -> None:
        pass

    # *** BUILT-INS ***

    def __init__(self, game_id):
        super().__init__()
        self._game_id : str  = game_id

    def __del__(self):
        self.Close()

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def Destination(self, mode:ExtractionMode):
        return self._destination(mode=mode)

    def WriteEventHeader(self, header:List[str]) -> None:
        self._writeEventsHeader(header=header)

    def WriteSessionHeader(self, header:List[str]) -> None:
        self._writeSessionHeader(header=header)

    def WritePlayerHeader(self, header:List[str]) -> None:
        self._writePlayerHeader(header=header)

    def WritePopulationHeader(self, header:List[str]) -> None:
        self._writePopulationHeader(header=header)

    def WriteEventLines(self, events:List[str]) -> None:
        self._writeEventLines(events=events)
        Logger.Log(f"Wrote ")

    def WriteSessionLines(self, sessions:List[ExportRow]) -> None:
        self._writeSessionLines(sessions=sessions)

    def WritePlayerLines(self, players:List[ExportRow]) -> None:
        self._writePlayerLines(players=players)

    def WritePopulationLines(self, populations:List[ExportRow]) -> None:
        self._writePopulationLines(populations=populations)

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
