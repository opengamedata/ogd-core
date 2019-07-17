## import standard libraries
import json
import logging
import typing
## import local files
import GameTable
from feature_extractors.WaveExtractor import WaveExtractor
from schemas.Schema import Schema

""" Class to extract and manage features for a processed csv file. """
class ProcManager:
    def __init__(self, ExtractorClass: type, game_table: GameTable, game_schema: Schema,
                 proc_csv_file: typing.IO.writable):
        ## Define instance vars
        self._ExtractorClass:     type               = ExtractorClass
        self._game_table:         GameTable          = game_table
        self._game_schema:        Schema             = game_schema
        self._proc_file:          typing.IO.writable = proc_csv_file
        self._session_extractors: typing.Dict[str, self._ExtractorClass] = {}

    def ProcessRow(self, row: typing.Tuple):
        session_id = row[self._game_table.session_id_index]
        col = row[self._game_table.complex_data_index]
        complex_data_parsed = json.loads(col) if (col is not None) else {"event_custom":row[self._game_table.event_index]}
        ## ensure we have an extractor for the given session:
        if not session_id in self._session_extractors.keys():
            self._session_extractors[session_id] = self._ExtractorClass(session_id, self._game_table, self._game_schema)
        ## do the actual extraction.
        self._session_extractors[session_id].extractFromRow( \
            row[self._game_table.level_index], complex_data_parsed, row[self._game_table.client_time_index] \
            )

    """ Empty the list of lines stored by the ProcManager.
        This is helpful if we're processing a lot of data and want to avoid
        Eating too much memory. """
    def ClearLines(self):
        logging.debug(f"Clearing {len(self._session_extractors)} entries from ProcManager.")
        self._session_extractors = {}

    def calculateAggregateFeatures(self):
        for extractor in self._session_extractors.values():
            extractor.calculateAggregateFeatures()

    """ Function to write out the header for a processed csv file.
        The corresponding function should be a static member of each extractor class.
        So, use whatever extractor class the manager was created to work with."""
    def WriteProcCSVHeader(self):
        self._ExtractorClass.writeCSVHeader(game_table=self._game_table, game_schema=self._game_schema, file=self._proc_file)

    def WriteProcCSVLines(self):
        for extractor in self._session_extractors.values():
            extractor.writeCurrentFeatures(file=self._proc_file)