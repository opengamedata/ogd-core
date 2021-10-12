# import standard libraries
from games.LAKELAND.LakelandExtractor import LakelandExtractor
from extractors.Extractor import Extractor
import logging
import sys
import traceback
import typing
from typing import Any, List, Type, Union
# import local files
import utils
from managers.FileManager import FileManager
from schemas.Event import Event
from schemas.GameSchema import GameSchema
from schemas.TableSchema import TableSchema

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
    def __init__(self, ExtractorClass: Type[Extractor], game_schema: GameSchema):
        ## Define instance vars
        self._ExtractorClass     :Type[Extractor]      = ExtractorClass
        self._game_schema        :GameSchema           = game_schema
        self._session_extractor  :Extractor            = self._ExtractorClass(session_id="population", game_schema=self._game_schema)

    ## Function to handle processing of a single row of data.
    #  Basically just responsible for ensuring an extractor for the session
    #  corresponding to the row already exists, then delegating the processing
    #  to that extractor.
    #  @param row_with_complex_parsed A tuple of the row data. We assume the
    #                      event_data_complex has already been parsed from JSON.
    def ProcessEvent(self, event: Event):
        # ensure we have an extractor for the given session:
        self._session_extractor.ExtractFromEvent(event=event)

    ##  Function to empty the list of lines stored by the PopulationProcessor.
    #   This is helpful if we're processing a lot of data and want to avoid
    #   eating too much memory.
    def ClearLines(self):
        utils.Logger.toStdOut(f"Clearing population entries from PopulationProcessor.", logging.DEBUG)
        self._session_extractor = self._ExtractorClass(session_id="population", game_schema=self._game_schema)

    def GetPopulationFeatures(self) -> List[Any]:
        return self._session_extractor.GetCurrentFeatures()

    def GetPopulationFeatureNames(self) -> List[str]:
        return Extractor._genFeatureNames(self._game_schema)

    ## Function to calculate aggregate features of all extractors created by the
    #  PopulationProcessor. Just calls the function once on each extractor.
    def CalculateAggregateFeatures(self):
        self._session_extractor.CalculateAggregateFeatures()

    ## Function to write out the header for a processed csv file.
    #  Just runs the header writer for whichever Extractor subclass we were given.
    def WritePopulationFileHeader(self, file_mgr:FileManager, separator:str="\t"):
        self._ExtractorClass.WriteFileHeader(game_schema=self._game_schema, file=file_mgr.GetPopulationFile(), separator=separator)

    ## Function to write out all data for the extractors created by the
    #  PopulationProcessor. Just calls the "write" function once for each extractor.
    def WritePopulationFileLines(self, file_mgr:FileManager, separator:str="\t"):
        self._session_extractor.WriteCurrentFeatures(file=file_mgr.GetPopulationFile(), separator=separator)