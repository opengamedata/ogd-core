# import standard libraries
from extractors.Extractor import Extractor
import json
import logging
import traceback
import typing
from typing import Dict, Tuple
# import local files
import utils
from schemas.Event import Event
from schemas.GameSchema import GameSchema
from schemas.TableSchema import TableSchema

## @class SessionProcessor
#  Class to extract and manage features for a processed csv file.
class SessionProcessor:
    ## Constructor for the SessionProcessor class.
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
    def __init__(self, ExtractorClass: type, table_schema: TableSchema, game_schema: GameSchema,
                 sessions_csv_file: typing.IO[str]):
        ## Define instance vars
        self._ExtractorClass:     type                            = ExtractorClass
        self._table_schema:         TableSchema                     = table_schema
        self._game_schema:        GameSchema                      = game_schema
        self._sessions_file:      typing.IO[str]                  = sessions_csv_file
        self._session_extractors: Dict[str, Extractor] = {}

    ## Function to handle processing of a single row of data.
    #  Basically just responsible for ensuring an extractor for the session
    #  corresponding to the row already exists, then delegating the processing
    #  to that extractor.
    #  @param row_with_complex_parsed A tuple of the row data. We assume the
    #                      event_data_complex has already been parsed from JSON.
    def ProcessRow(self, event: Event):
        # ensure we have an extractor for the given session:
        if not event.session_id in self._session_extractors.keys():
            if event.app_id == 'LAKELAND':
                self._session_extractors[event.session_id] = self._ExtractorClass(session_id=event.session_id, game_id=self._game_schema, session_file=self._sessions_file)
            else:
                self._session_extractors[event.session_id] = self._ExtractorClass(session_id=event.session_id, game_schema=self._game_schema)
        self._session_extractors[event.session_id].extractFromRow(event, self._table_schema)

    ##  Function to empty the list of lines stored by the SessionProcessor.
    #   This is helpful if we're processing a lot of data and want to avoid
    #   eating too much memory.
    def ClearLines(self):
        utils.Logger.toStdOut(f"Clearing {len(self._session_extractors)} entries from SessionProcessor.", logging.DEBUG)
        self._session_extractors = {}

    ## Function to calculate aggregate features of all extractors created by the
    #  SessionProcessor. Just calls the function once on each extractor.
    def calculateAggregateFeatures(self):
        for extractor in self._session_extractors.values():
            extractor.calculateAggregateFeatures()

    ## Function to write out the header for a processed csv file.
    #  Just runs the header writer for whichever Extractor subclass we were given.
    def WriteSessionCSVHeader(self):
        self._ExtractorClass.writeCSVHeader(game_schema=self._game_schema, file=self._sessions_file)

    ## Function to write out all data for the extractors created by the
    #  SessionProcessor. Just calls the "write" function once for each extractor.
    def WriteSessionCSVLines(self):
        for extractor in self._session_extractors.values():
            extractor.writeCurrentFeatures(file=self._sessions_file)