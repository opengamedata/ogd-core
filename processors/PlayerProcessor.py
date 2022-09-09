# import standard libraries
import logging
import traceback
from typing import List, Dict, Type, Optional, Set
# import local files
from extractors.ExtractorLoader import ExtractorLoader
from extractors.registries.FeatureRegistry import FeatureRegistry
from processors.FeatureProcessor import FeatureProcessor
from processors.SessionProcessor import SessionProcessor
from schemas.Event import Event
from schemas.ExportMode import ExportMode
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
from schemas.GameSchema import GameSchema
from utils import Logger, ExportRow

## @class PlayerProcessor
#  Class to extract and manage features for a processed csv file.
class PlayerProcessor(FeatureProcessor):

    # *** BUILT-INS ***

    ## Constructor for the PlayerProcessor class.
    def __init__(self, LoaderClass: Type[ExtractorLoader], game_schema: GameSchema, player_id:str,
                 feature_overrides:Optional[List[str]]=None):
        """Constructor for the PlayerProcessor class.
           Simply stores some data for use later, including the type of extractor to use.

        :param LoaderClass: The type of data extractor to use for input data.
                            This should correspond to whatever game_id is in the TableSchema.
        :type LoaderClass: Type[ExtractorLoader]
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
        self._player_id : str = player_id
        super().__init__(LoaderClass=LoaderClass, game_schema=game_schema, feature_overrides=feature_overrides)
        ## Define instance vars
        Logger.Log(f"Done", logging.DEBUG, depth=2)

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

    def _getExtractorNames(self) -> List[str]:
        if isinstance(self._registry, FeatureRegistry):
            return ["PlayerID"] + self._registry.GetExtractorNames()
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
        self._registry.ExtractFromEvent(event=event)

    def _getFeatureValues(self, as_str:bool=False) -> ExportRow:
        ret_val : ExportRow
        if as_str:
            ret_val = [self._player_id] + self._registry.GetFeatureStringValues()
        else:
            ret_val = [self._player_id] + self._registry.GetFeatureValues()
        return ret_val

    def _getFeatureData(self, order:int) -> Dict[str, List[FeatureData]]:
        ret_val : Dict[str, List[FeatureData]] = { "players":[] }
        ret_val["players"] = self._registry.GetFeatureData(order=order, player_id=self._player_id)
        return ret_val

    ##  Function to empty the list of lines stored by the PlayerProcessor.
    def _clearLines(self) -> None:
        """Function to empty the list of lines stored by the PlayerProcessor.
        This is helpful if we're processing a lot of data and want to avoid eating too much memory.
        """
        Logger.Log(f"Clearing features from PlayerProcessor for {self._player_id}.", logging.DEBUG, depth=2)
        self._registry = FeatureRegistry(mode=self._mode)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
