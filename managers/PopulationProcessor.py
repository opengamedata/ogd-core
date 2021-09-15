# import standard libraries
from games.LAKELAND.LakelandExtractor import LakelandExtractor
from extractors.Extractor import Extractor
import json
import logging
import traceback
import typing
from typing import Dict, Type
# import local files
import utils
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
    def __init__(self, ExtractorClass: Type[Extractor], table_schema: TableSchema, game_schema: GameSchema,
                 sessions_file: typing.IO[str], separator:str = "\t"):
        ## Define instance vars
        self._ExtractorClass     :Type[Extractor]      = ExtractorClass
        self._table_schema       :TableSchema          = table_schema
        self._game_schema        :GameSchema           = game_schema
        self._sessions_file      :typing.IO[str]       = sessions_file
        self._session_extractor  :Extractor            = self._ExtractorClass(session_id="population", game_schema=self._game_schema)
        self._separator          :str                  = separator

    ## Function to handle processing of a single row of data.
    #  Basically just responsible for ensuring an extractor for the session
    #  corresponding to the row already exists, then delegating the processing
    #  to that extractor.
    #  @param row_with_complex_parsed A tuple of the row data. We assume the
    #                      event_data_complex has already been parsed from JSON.
    def ProcessEvent(self, event: Event):
        # ensure we have an extractor for the given session:
        self._session_extractor.ExtractFromEvent(event=event, table_schema=self._table_schema)

    ##  Function to empty the list of lines stored by the PopulationProcessor.
    #   This is helpful if we're processing a lot of data and want to avoid
    #   eating too much memory.
    def ClearLines(self):
        utils.Logger.toStdOut(f"Clearing population entries from PopulationProcessor.", logging.DEBUG)
        self._session_extractor = self._ExtractorClass(session_id="population", game_schema=self._game_schema)

    def GetPopulationFeatures(self):
        return self._session_extractor.GetCurrentFeatures()

    ## Function to calculate aggregate features of all extractors created by the
    #  PopulationProcessor. Just calls the function once on each extractor.
    def CalculateAggregateFeatures(self):
        self._session_extractor.CalculateAggregateFeatures()

    ## Function to write out the header for a processed csv file.
    #  Just runs the header writer for whichever Extractor subclass we were given.
    def WriteSessionFileHeader(self):
        self._ExtractorClass.WriteFileHeader(game_schema=self._game_schema, file=self._sessions_file, separator=self._separator)

    ## Function to write out all data for the extractors created by the
    #  PopulationProcessor. Just calls the "write" function once for each extractor.
    def WriteSessionFileLines(self):
        self._session_extractor.WriteCurrentFeatures(file=self._sessions_file)