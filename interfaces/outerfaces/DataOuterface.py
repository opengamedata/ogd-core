## import standard libraries
import abc
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union

# import local files
from interfaces.Interface import Interface
from schemas.IDMode import IDMode
from schemas.ExportMode import ExportMode
from utils import Logger, ExportRow

class DataOuterface(Interface):

    # *** ABSTRACTS ***

    @abc.abstractmethod
    def _destination(self, mode:ExportMode) -> str:
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
    def _writeEventLines(self, events:List[ExportRow]) -> None:
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

    def Destination(self, mode:ExportMode):
        return self._destination(mode=mode)

    def WriteEventHeader(self, header:List[str]) -> None:
        self._writeEventsHeader(header=header)

    def WriteSessionHeader(self, header:List[str]) -> None:
        self._writeSessionHeader(header=header)

    def WritePlayerHeader(self, header:List[str]) -> None:
        self._writePlayerHeader(header=header)

    def WritePopulationHeader(self, header:List[str]) -> None:
        self._writePopulationHeader(header=header)

    def WriteEventLines(self, events:List[ExportRow]) -> None:
        self._writeEventLines(events=events)
        Logger.Log(f"Wrote {len(events)} events to {self.Destination(mode=ExportMode.EVENTS)}", logging.INFO, depth=2)

    def WriteSessionLines(self, sessions:List[ExportRow]) -> None:
        self._writeSessionLines(sessions=sessions)
        Logger.Log(f"Wrote {len(sessions)} events to {self.Destination(mode=ExportMode.SESSION)}", logging.INFO, depth=2)

    def WritePlayerLines(self, players:List[ExportRow]) -> None:
        self._writePlayerLines(players=players)
        Logger.Log(f"Wrote {len(players)} events to {self.Destination(mode=ExportMode.PLAYER)}", logging.INFO, depth=2)

    def WritePopulationLines(self, populations:List[ExportRow]) -> None:
        self._writePopulationLines(populations=populations)
        Logger.Log(f"Wrote {len(populations)} events to {self.Destination(mode=ExportMode.POPULATION)}", logging.INFO, depth=2)

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
