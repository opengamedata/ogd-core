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

class DebugOuterface(DataOuterface):

    # *** BUILT-INS ***

    def __init__(self, game_id:str):
        super().__init__(game_id=game_id, config={})
        self.Open()

    def __del__(self):
        self.Close()

    # *** IMPLEMENT ABSTRACTS ***

    def _open(self) -> bool:
        self._display(f"Using a debug outerface to view OGD output for {self._game_id}.")
        return True

    def _close(self) -> bool:
        self._display(f"No longer using a debug outerface to view OGD output for {self._game_id}.")
        return True

    def _destination(self, mode:ExportMode) -> str:
        return "Logger.Log"

    def _removeExportMode(self, mode:ExportMode):
        if mode == ExportMode.EVENTS:
            self._display("No longer outputting event data to debug stream.")
        elif mode == ExportMode.SESSION:
            self._display("No longer outputting session data to debug stream.")
        elif mode == ExportMode.PLAYER:
            self._display("No longer outputting player data to debug stream.")
        elif mode == ExportMode.POPULATION:
            self._display("No longer outputting population data to debug stream.")

    def _writeEventsHeader(self, header:List[str]) -> None:
        self._display("Events header:")
        self._display(header)

    def _writeSessionHeader(self, header:List[str]) -> None:
        self._display("Sessions header:")
        self._display(header)

    def _writePlayerHeader(self, header:List[str]) -> None:
        self._display("Player header:")
        self._display(header)

    def _writePopulationHeader(self, header:List[str]) -> None:
        self._display("Population header:")
        self._display(header)

    def _writeEventLines(self, events:List[ExportRow]) -> None:
        self._display("Event data:")
        _lengths = [len(elem) for elem in events]
        self._display(f"{len(events)} events, average length {sum(_lengths) / len(_lengths)}")

    def _writeSessionLines(self, sessions:List[ExportRow]) -> None:
        self._display("Session data:")
        _lengths = [len(elem) for elem in sessions]
        self._display(f"{len(sessions)} events, average length {sum(_lengths) / len(_lengths)}")

    def _writePlayerLines(self, players:List[ExportRow]) -> None:
        self._display("Player data:")
        _lengths = [len(elem) for elem in players]
        self._display(f"{len(players)} events, average length {sum(_lengths) / len(_lengths)}")

    def _writePopulationLines(self, populations:List[ExportRow]) -> None:
        self._display("Population data:")
        _lengths = [len(elem) for elem in populations]
        self._display(f"{len(populations)} events, average length {sum(_lengths) / len(_lengths)}")

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _display(self, msg):
        Logger.Log(f"DebugOuterface: {msg}", logging.DEBUG)
