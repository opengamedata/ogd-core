# import standard libraries
import logging
from datetime import datetime
from typing import Any, Dict, List, Type, Optional, Set
# import local files
from schemas.FeatureData import FeatureData
from extractors.ExtractorLoader import ExtractorLoader
from extractors.registries.FeatureRegistry import FeatureRegistry
from processors.FeatureProcessor import FeatureProcessor
from processors.PlayerProcessor import PlayerProcessor
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.ExportMode import ExportMode
from schemas.GameSchema import GameSchema
from utils import Logger, ExportRow

## @class PopulationProcessor
#  Class to extract and manage features for a processed csv file.
class PopulationProcessor(FeatureProcessor):

    # *** BUILT-INS ***

    ## Constructor for the PopulationProcessor class.
    def __init__(self, LoaderClass: Type[ExtractorLoader], game_schema: GameSchema,
                 feature_overrides:Optional[List[str]]=None):
        """Constructor for the PopulationProcessor class.
        Simply stores some data for use later, including the type of extractor to use.

        :param LoaderClass: The type of data extractor to use for input data.
                            This should correspond to whatever game_id is in the TableSchema.
        :type LoaderClass: Type[ExtractorLoader]
        :param game_schema: A dictionary that defines how the game data itself is structured.
        :type game_schema: GameSchema
        :param feature_overrides: _description_, defaults to None
        :type feature_overrides: Optional[List[str]], optional
        :param pop_file: _description_, defaults to None
        :type pop_file: Optional[IO[str]], optional
        """
        super().__init__(LoaderClass=LoaderClass, game_schema=game_schema, feature_overrides=feature_overrides)

    def __str__(self):
        return f"PopulationProcessor"

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def _mode(self) -> ExtractionMode:
        return ExtractionMode.POPULATION

    @property
    def _playerID(self) -> str:
        return "population"

    @property
    def _sessionID(self) -> str:
        return "population"

    def _getExtractorNames(self) -> List[str]:
        if isinstance(self._registry, FeatureRegistry):
            return self._registry.GetExtractorNames()
        else:
            raise TypeError("PopulationProcessor's registry is not a FeatureRegistry!")

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
            ret_val = self._registry.GetFeatureStringValues()
        else:
            ret_val = self._registry.GetFeatureValues()
        return ret_val

    def _getFeatureData(self, order:int) -> List[FeatureData]:
        return self._registry.GetFeatureData(order=order)

    ##  Function to empty the list of lines stored by the PopulationProcessor.
    #   This is helpful if we're processing a lot of data and want to avoid
    #   eating too much memory.
    def _clearLines(self) -> None:
        Logger.Log(f"Clearing features from PopulationProcessor.", logging.DEBUG, depth=2)
        self._registry = FeatureRegistry(mode=self._mode)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***