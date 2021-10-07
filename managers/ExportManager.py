## @package DataToCSV.py
#  A package to handle processing of stuff from our database,
#  for export to CSV files.

## import standard libraries
from extractors.Extractor import Extractor
import logging
import math
import os
import subprocess
import traceback
from datetime import datetime
from typing import List, Type, Tuple, Union
## import local files
import utils
from config.config import settings
from managers.FileManager import *
from managers.PopulationProcessor import PopulationProcessor
from managers.SessionProcessor import SessionProcessor
from managers.EventProcessor import EventProcessor
from managers.Request import Request
from schemas.GameSchema import GameSchema
from schemas.TableSchema import TableSchema
from games.AQUALAB.AqualabExtractor import AqualabExtractor
from games.CRYSTAL.CrystalExtractor import CrystalExtractor
from games.JOWILDER.JowilderExtractor import JowilderExtractor
from games.LAKELAND.LakelandExtractor import LakelandExtractor
from games.MAGNET.MagnetExtractor import MagnetExtractor
from games.SHADOWSPECT.ShadowspectExtractor import ShadowspectExtractor
from games.WAVES.WaveExtractor import WaveExtractor

## @class ExportManager
#  A class to export features and raw data, given a Request object.
class ExportManager:
    ## Constructor for the ExportManager class.
    #  Fairly simple, just saves some data for later use during export.
    #  @param game_id Initial id of game to export
    #                 (this can be changed, if a TableSchema with a different id is
    #                  given, but will generate a warning)
    #  @param db      An active database connection
    #  @param settings A dictionary of program settings, some of which are needed for export.
    def __init__(self, game_id: str, settings):
        self._game_id:    str
        if game_id is None:
            utils.Logger.toStdOut("Game ID was not given!", logging.ERROR)
        else:
            self._game_id   = game_id
        self._settings = settings

    def ExecuteRequest(self, request:Request, game_schema:GameSchema, table_schema:TableSchema) -> bool:
        ret_val : bool

        start = datetime.now()
        if request.GetGameID() != self._game_id:
            utils.Logger.toFile(f"Changing ExportManager game from {self._game_id} to {request.GetGameID()}", logging.WARNING)
            self._game_id = request.GetGameID()
        if self._executeRequest(request=request, game_schema=game_schema, table_schema=table_schema):
            utils.Logger.Log(f"Successfully completed request {str(request)}.", logging.INFO)
            ret_val = True
        else:
            utils.Logger.Log(f"Could not complete request {str(request)}", logging.ERROR)
            ret_val = False
        time_delta = datetime.now() - start
        utils.Logger.Log(f"Total Data Request Execution Time: {time_delta}", logging.INFO)

        return ret_val

    ## Private function containing most of the code to handle processing of db
    #  data, and export to files.
    #  @param request    A data structure carrying parameters for feature extraction
    #                    and export
    #  @param game_table A data structure containing information on how the db
    #                    table assiciated with the given game is structured. 
    def _executeRequest(self, request:Request, game_schema:GameSchema, table_schema:TableSchema) -> bool:
        ret_val = False
        try:
            # 1) Prepare extractor, if game doesn't have an extractor, make sure we don't try to export it.
            game_extractor : Union[Type[Extractor],None] = self._prepareExtractor()
            if game_extractor is None:
                request._files.sessions = False
                request._files.population = False
            # 2) Prepare files for export.
            file_manager = FileManager(exporter_files=request._files, game_id=self._game_id, \
                                       data_dir=self._settings["DATA_DIR"], date_range=request._range.GetDateRange(),
                                       extension="tsv")
            # If we have a schema, we can do feature extraction.
            if game_schema is not None:
                # 3) Loop over data, running extractors.
                file_manager.OpenFiles()
                num_sess: int = self._exportToFiles(request=request, game_extractor=game_extractor, file_manager=file_manager,\
                                    game_schema=game_schema, table_schema=table_schema)
                # 4) Save and close files
                try:
                    # before we zip stuff up, let's ensure the readme is in place:
                    readme = open(file_manager._readme_path, mode='r')
                except FileNotFoundError:
                    utils.Logger.Log(f"Missing readme for {self._game_id}, generating new readme...", logging.WARNING)
                    readme_path = Path("./data") / self._game_id
                    utils.GenerateReadme(game_name=self._game_id, game_schema=game_schema, column_list=table_schema.ColumnList(), path=readme_path)
                file_manager.CloseFiles()
                file_manager.ZipFiles()
                # 5) Finally, update the list of csv files.
                file_manager.WriteMetadataFile(num_sess=num_sess)
                file_manager.UpdateFileExportList(num_sess=num_sess)
                ret_val = True
            else:
                utils.Logger.Log(f"Missing schema for {request.GetGameID()}")
        except Exception as err:
            msg = f"{type(err)} {str(err)}"
            utils.Logger.toStdOut(msg, logging.ERROR)
            traceback.print_tb(err.__traceback__)
            utils.Logger.toFile(msg, logging.ERROR)
        finally:
            return ret_val

    def _exportToFiles(self, request:Request, game_extractor:Union[Type[Extractor],None], file_manager:FileManager, game_schema: GameSchema, table_schema: TableSchema):
        ret_val = -1
        # 2) Set up processors.
        pop_processor = sess_processor = evt_processor = None
        if request._files.events:
            evt_file = file_manager.GetEventsFile()
            if evt_file is not None:
                evt_processor = EventProcessor()
                evt_processor.WriteEventsCSVHeader(file_mgr=file_manager, separator="\t")
        else:
            utils.Logger.Log("Event log not requested, skipping events file.", logging.INFO)
        if game_extractor is not None:
            if request._files.sessions:
                sess_processor = SessionProcessor(ExtractorClass=game_extractor, game_schema=game_schema)
                sess_processor.WriteSessionFileHeader(file_mgr=file_manager, separator="\t")
            else:
                utils.Logger.Log("Session features not requested, skipping session_features file.", logging.INFO)
            if request._files.population:
                pop_processor = PopulationProcessor(ExtractorClass=game_extractor, game_schema=game_schema)
                pop_processor.WritePopulationFileHeader(file_mgr=file_manager, separator="\t")
            else:
                utils.Logger.Log("Population features not requested, skipping population_features file.", logging.INFO)
        else:
            utils.Logger.Log("Could not export population/session data, no game extractor given!", logging.WARN)
        # 2) Get the IDs of sessions to process
        _dummy = request.RetrieveSessionIDs()
        sess_ids = _dummy if _dummy is not None else []
        ret_val = len(sess_ids)
        utils.Logger.toStdOut(f"Preparing to process {len(sess_ids)} sessions.", logging.INFO)
        # 3) Loop over and process the sessions, slice-by-slice (where each slice is a list of sessions).
        session_slices = self._genSlices(sess_ids)
        for i, next_slice in enumerate(session_slices):
            next_data_set : Union[List[Tuple],None] = request._interface.RowsFromIDs(next_slice)
            if next_data_set is not None:
                start      : datetime = datetime.now()
                num_events : int      = len(next_data_set)
                try:
                    # 3a) If next slice yielded valid data from the interface, process row-by-row.
                    for row in next_data_set:
                        next_event = table_schema.RowToEvent(row)
                        if next_event.session_id in sess_ids:
                            if pop_processor is not None:
                                pop_processor.ProcessEvent(next_event)
                            if sess_processor is not None:
                                sess_processor.ProcessEvent(next_event)
                            if evt_processor is not None:
                                evt_processor.ProcessEvent(next_event)
                        else:
                            utils.Logger.Log(f"Found a session ({next_event.session_id}) which was in the slice but not in the list of sessions for processing.", logging.WARNING)
                    # 3b) After processing all rows for each slice, write out the session data and reset for next slice.
                    if request._files.events and evt_processor is not None:
                        evt_processor.WriteEventsCSVLines(file_mgr=file_manager)
                        evt_processor.ClearLines()
                    if request._files.sessions and sess_processor is not None:
                        sess_processor.CalculateAggregateFeatures()
                        sess_processor.WriteSessionFileLines(file_mgr=file_manager, separator="\t")
                        sess_processor.ClearLines()
                except Exception as err:
                    msg = f"Error while processing slice [{i+1}/{len(session_slices)}]"
                    raise err
                time_delta = datetime.now() - start
                utils.Logger.Log(f"Processing time for slice [{i+1}/{len(session_slices)}]: {time_delta} to handle {num_events} events", logging.INFO)
            else:
                utils.Logger.Log(f"Could not retrieve data set for slice [{i+1}/{len(session_slices)}].", logging.WARN)
        # 4) If we made it all the way to the end, write population data and return the number of sessions processed.
        if request._files.population and pop_processor is not None:
            pop_processor.WritePopulationFileLines(file_mgr=file_manager)
            pop_processor.ClearLines()
        return ret_val

    def _prepareExtractor(self) -> Union[Type[Extractor],None]:
        game_extractor: Union[type,None] = None
        if self._game_id == "AQUALAB":
            game_extractor = AqualabExtractor
        elif self._game_id == "CRYSTAL":
            game_extractor = CrystalExtractor
        elif self._game_id == "JOWILDER":
            game_extractor = JowilderExtractor
        elif self._game_id == "LAKELAND":
            game_extractor = LakelandExtractor
        elif self._game_id == "MAGNET":
            game_extractor = MagnetExtractor
        elif self._game_id == "SHADOWSPECT":
            game_extractor = ShadowspectExtractor
        elif self._game_id == "WAVES":
            game_extractor = WaveExtractor
        elif self._game_id in ["BACTERIA", "BALLOON", "CYCLE_CARBON", "CYCLE_NITROGEN", "CYCLE_WATER", "EARTHQUAKE", "STEMPORTS", "WIND"]:
            # all games with data but no extractor.
            pass
        else:
            raise Exception(f"Got an invalid game ID ({self._game_id})!")
        return game_extractor

    def _genSlices(self, sess_ids):
        _sess_ct = len(sess_ids)
        _slice_size = self._settings["BATCH_SIZE"]
        return [[sess_ids[i] for i in range( j*_slice_size, min((j+1)*_slice_size, _sess_ct) )]
                                       for j in range( 0, math.ceil(_sess_ct / _slice_size) )]
