# import standard libraries
import logging
import traceback
from typing import List, Dict, Type, Optional, Set
# import local files
from ogd.core.generators.GeneratorLoader import GeneratorLoader
from ogd.core.registries.ExtractorRegistry import ExtractorRegistry
from ogd.core.processors.ExtractorProcessor import ExtractorProcessor
from ogd.core.processors.SessionProcessor import SessionProcessor
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExportMode import ExportMode
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.schemas.games.GameSchema import GameSchema
from ogd.core.utils.Logger import Logger
from ogd.core.utils.utils import ExportRow

## @class PlayerProcessor
#  Class to extract and manage features for a processed csv file.
class PlayerProcessor(ExtractorProcessor):

    # *** BUILT-INS & PROPERTIES ***

    ## Constructor for the PlayerProcessor class.
    def __init__(self, LoaderClass: Type[GeneratorLoader], game_schema: GameSchema, player_id:str,
                 feature_overrides:Optional[List[str]]=None):
        """Constructor for the PlayerProcessor class.
           Simply stores some data for use later, including the type of extractor to use.

        :param LoaderClass: The type of data extractor to use for input data.
                            This should correspond to whatever game_id is in the TableSchema.
        :type LoaderClass: Type[GeneratorLoader]
        :param game_schema: A dictionary that defines how the game data itself is structured.
        :type game_schema: GameSchema
        :param player_id: _description_
        :type player_id: str
        :param feature_overrides: _description_, defaults to None
        :type feature_overrides: Union[List[str],None], optional
        :param player_file: _description_, defaults to None
        :type player_file: Optional[IO[str]], optional
        """
        Logger.Log(f"Setting up PlayerProcessor for {player_id}...", logging.DEBUG, depth=2)
        self._player_id : str      = player_id
        self._sessions  : Set[str] = set()
        super().__init__(LoaderClass=LoaderClass, game_schema=game_schema, feature_overrides=feature_overrides)
        ## Define instance vars
        Logger.Log(f"Done", logging.DEBUG, depth=2)

    def __str__(self):
        return f"PlayerProcessor({self._player_id})"

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def _mode(self) -> ExtractionMode:
        return ExtractionMode.PLAYER

    @property
    def _playerID(self) -> str:
        return self._player_id

    @property
    def _sessionID(self) -> str:
        return "player"

    def _getGeneratorNames(self) -> List[str]:
        if isinstance(self._registry, ExtractorRegistry):
            return ["PlayerID", "SessionCount"] + self._registry.GetGeneratorNames()
        else:
            raise TypeError()

    ## Function to handle processing of a single row of data.
    def _processEvent(self, event:Event):
        """Function to handle processing of a single row of data.
        Basically just responsible for ensuring an extractor for the session corresponding
        to the row already exists, then delegating the processing to that extractor.
        :param event: An object with the data for the event to be processed.
        :type event: Event
        """
        self._sessions.add(event.SessionID)
        self._registry.UpdateFromEvent(event=event)

    def _getLines(self) -> List[ExportRow]:
        ret_val : ExportRow
        # if as_str:
        #     ret_val = [self._player_id, len(self._sessions)] + self._registry.GetFeatureStringValues()
        # else:
        ret_val = [self._player_id, len(self._sessions)] + self._registry.GetFeatureValues()
        return [ret_val]

    def _getFeatureData(self, order:int) -> List[FeatureData]:
        return self._registry.GetFeatureData(order=order, player_id=self._player_id)

    ##  Function to empty the list of lines stored by the PlayerProcessor.
    def _clearLines(self) -> None:
        """Function to empty the list of lines stored by the PlayerProcessor.
        This is helpful if we're processing a lot of data and want to avoid eating too much memory.
        """
        Logger.Log(f"Clearing features from PlayerProcessor for {self._player_id}.", logging.DEBUG, depth=2)
        self._registry = ExtractorRegistry(mode=self._mode)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
