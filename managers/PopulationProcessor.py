# import standard libraries
import logging
import sys
import traceback
import typing
from typing import Any, IO, List, Type, Union
# import local files
import utils
from extractors.Extractor import Extractor
from games.LAKELAND.LakelandExtractor import LakelandExtractor
from managers.FileManager import FileManager
from schemas.Event import Event
from schemas.GameSchema import GameSchema

## @class PopulationProcessor
#  Class to extract and manage features for a processed csv file.
class PopulationProcessor:
    ## Constructor for the PopulationProcessor class.
    #  Simply stores some data for use later, including the type of extractor to
    #  use.
    #
    #  @param ExtractorClass The type of data extractor to use for input data.
    #         This should correspond to whatever game_id is in the TableSchema.
    #  @param game_table    A data structure containing information on how the db
    #                       table assiciated with the given game is structured. 
    #  @param game_schema   A dictionary that defines how the game data itself
    #                       is structured.
    #  @param sessions_csv_file The output file, to which we'll write the processed
    #                       feature data.
    def __init__(self, ExtractorClass: Type[Extractor], game_schema: GameSchema, feature_overrides:Union[List[str],None]=None, pop_file:IO[str]=sys.stdout):
        ## Define instance vars
        self._ExtractorClass   : Type[Extractor] = ExtractorClass
        self._game_schema      : GameSchema      = game_schema
        self._extractor        : Extractor
        self._sess_encountered : set             = set()
        self._overrides        : Union[List[str],None] = feature_overrides
        if self._ExtractorClass is LakelandExtractor:
            self._extractor = LakelandExtractor(session_id="population", game_schema=self._game_schema, feature_overrides=self._overrides, sessions_file=pop_file)
        else:
            self._extractor = self._ExtractorClass(session_id="population", game_schema=self._game_schema, feature_overrides=feature_overrides)

    ## Function to handle processing of a single row of data.
    #  Basically just responsible for ensuring an extractor for the session
    #  corresponding to the row already exists, then delegating the processing
    #  to that extractor.
    #  @param row_with_complex_parsed A tuple of the row data. We assume the
    #                      event_data_complex has already been parsed from JSON.
    def ProcessEvent(self, event: Event):
        # ensure we have an extractor for the given session:
        self._sess_encountered.add(event.session_id)
        self._extractor.ExtractFromEvent(event=event)

    ## Function to calculate aggregate features of all extractors created by the
    #  PopulationProcessor. Just calls the function once on each extractor.
    def CalculateAggregateFeatures(self):
        self._extractor.CalculateAggregateFeatures()

    def GetPopulationFeatureNames(self) -> List[str]:
        return self._extractor.GetFeatureNames(self._game_schema, overrides=self._overrides) + ["SessionCount"]

    def GetPopulationFeatures(self) -> List[Any]:
        return self._extractor.GetFeatureValues() + [len(self._sess_encountered)]

    ## Function to write out the header for a processed csv file.
    #  Just runs the header writer for whichever Extractor subclass we were given.
    def WritePopulationFileHeader(self, file_mgr:FileManager, separator:str="\t"):
        self._extractor.WriteFileHeader(game_schema=self._game_schema, file=file_mgr.GetPopulationFile(), separator=separator)

    ## Function to write out all data for the extractors created by the
    #  PopulationProcessor. Just calls the "write" function once for each extractor.
    def WritePopulationFileLines(self, file_mgr:FileManager, separator:str="\t"):
        self._extractor.WriteFeatureValues(file=file_mgr.GetPopulationFile(), separator=separator)

    ##  Function to empty the list of lines stored by the PopulationProcessor.
    #   This is helpful if we're processing a lot of data and want to avoid
    #   eating too much memory.
    def ClearLines(self, pop_file:IO[str]=sys.stdout):
        utils.Logger.toStdOut(f"Clearing population entries from PopulationProcessor.", logging.DEBUG)
        if self._ExtractorClass is LakelandExtractor:
            self._extractor = LakelandExtractor(session_id="population", game_schema=self._game_schema, feature_overrides=self._overrides, sessions_file=pop_file)
        else:
            self._extractor = self._ExtractorClass(session_id="population", game_schema=self._game_schema, feature_overrides=self._overrides)