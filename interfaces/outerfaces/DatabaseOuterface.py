"""DataOuterface Module
"""
## import standard libraries
import abc
import logging
from typing import Any, Dict, List, Set

# import local files
from interfaces.outerfaces.DataOuterface import DataOuterface
from schemas.ExportMode import ExportMode
from schemas.configs.GameSourceSchema import GameSourceSchema
from utils import Logger

class DatabaseOuterface(DataOuterface):
    """Base class for feature and event output.

    :param Interface: _description_
    :type Interface: _type_
    :return: _description_
    :rtype: _type_
    """

    # *** ABSTRACTS ***

    @abc.abstractmethod
    def _setupEventTable(self) -> str:
        pass

    @abc.abstractmethod
    def _setupProcessedEventTable(self) -> str:
        pass

    @abc.abstractmethod
    def _setupFeaturesTable(self) -> str:
        pass

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, game_id, config:GameSourceSchema, export_modes:Set[ExportMode]):
        super().__init__(game_id=game_id, config=config, export_modes=export_modes)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _writeRawEventsHeader(self, header:List[str]) -> None:
        pass

    def _writeProcessedEventsHeader(self, header:List[str]) -> None:
        pass

    def _writeSessionHeader(self, header:List[str]) -> None:
        pass

    def _writePlayerHeader(self, header:List[str]) -> None:
        pass

    def _writePopulationHeader(self, header:List[str]) -> None:
        pass
