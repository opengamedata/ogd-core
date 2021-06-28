## @package DataToCSV.py
#  A package to handle processing of stuff from our database,
#  for export to CSV files.

## import standard libraries
import json
import logging
import math
import os
import subprocess
import traceback
import typing
import zipfile
import pandas as pd
from datetime import datetime
from typing import Tuple
## import local files
import utils
from config.config import settings
from interfaces.MySQLInterface import SQL
from interfaces.MySQLInterface import MySQLInterface
from managers.FileManager import *
from managers.SessionProcessor import SessionProcessor
from managers.EventProcessor import EventProcessor
from managers.Request import Request, ExporterFiles, ExporterRange
from schemas.Event import Event
from schemas.GameSchema import GameSchema
from schemas.TableSchema import TableSchema
from games.WAVES.WaveExtractor import WaveExtractor
from games.CRYSTAL.CrystalExtractor import CrystalExtractor
from games.LAKELAND.LakelandExtractor import LakelandExtractor
from games.JOWILDER.JowilderExtractor import JowilderExtractor
from games.MAGNET.MagnetExtractor import MagnetExtractor

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
        # self._select_queries = []

    def ExecuteRequest(self, request:Request, game_schema :GameSchema, table_schema:TableSchema):
        if request.GetGameID() != self._game_id:
            utils.Logger.toFile(f"Changing ExportManager game from {self._game_id} to {request.GetGameID()}", logging.WARNING)
            self._game_id = request.GetGameID()
        try:
            if self._executeRequest(request=request, table_schema=table_schema):
                utils.Logger.Log(f"Successfully completed request {str(request)}.", logging.INFO)
            else:
                utils.Logger.Log(f"Could not complete request {str(request)}", logging.ERROR)
        except Exception as err:
            msg = f"General error in ExecuteRequest: {type(err)} {str(err)}"
            SQL.server500Error(msg)
            utils.Logger.toFile(msg, logging.ERROR)
            traceback.print_tb(err.__traceback__)

    ## Private function containing most of the code to handle processing of db
    #  data, and export to files.
    #  @param request    A data structure carrying parameters for feature extraction
    #                    and export
    #  @param game_table A data structure containing information on how the db
    #                    table assiciated with the given game is structured. 
    def _executeRequest(self, request:Request, table_schema:TableSchema) -> bool:
        # utils.Logger.toStdOut(f"complex_data_index: {complex_data_index}", logging.DEBUG)
        ret_val = False
        try:
            # 2a) Prepare schema and extractor, if game doesn't have an extractor, make sure we don't try to export it.
            game_schema, game_extractor = self._prepareSchema()
            if game_extractor is None:
                request._files.sessions = False
            # 2b) Prepare files for export.
            file_manager = FileManager(exporter_files=request._files, game_id=self._game_id, \
                                       data_dir=self._settings["DATA_DIR"], date_range=request._range.GetDateRange())
            file_manager.OpenFiles()
            # If we have a schema, we can do feature extraction.
            if game_schema is not None:
                # 4) Loop over data, running extractors.
                start = datetime.now()

                num_sess: int = self._extractToCSVs(request=request, file_manager=file_manager,\
                                    game_schema=game_schema, table_schema=table_schema, game_extractor=game_extractor)

                time_delta = datetime.now() - start
                num_min = math.floor(time_delta.total_seconds()/60)
                num_sec = time_delta.total_seconds() % 60
                utils.Logger.Log(f"Total Data Extraction Time: {num_min} min, {num_sec:.3f} sec", logging.INFO)
                # 5) Save and close files
                # before we zip stuff up, let's ensure the readme is in place:
                try:
                    readme = open(file_manager._readme_path, mode='r')
                except FileNotFoundError:
                    utils.Logger.Log(f"Missing readme for {self._game_id}, generating new readme...", logging.WARNING)
                    utils.GenerateReadme(game_name=self._game_id, game_schema=game_schema, column_list=table_schema.ColumnList(), path=f"./data/{self._game_id}")
                file_manager.ZipFiles()
                # 6) Finally, update the list of csv files.
                file_manager.WriteMetadataFile(date_range=request._range.GetDateRange(), num_sess=num_sess)
                file_manager.UpdateFileExportList(date_range=request._range.GetDateRange(), num_sess=num_sess)
                ret_val = True
        except Exception as err:
            msg = f"{type(err)} {str(err)}"
            utils.Logger.toStdOut(msg, logging.ERROR)
            traceback.print_tb(err.__traceback__)
            utils.Logger.toFile(msg, logging.ERROR)
        finally:
            return ret_val

    def _prepareSchema(self) -> Tuple[GameSchema, Union[type,None]]:
        game_extractor: Union[type,None] = None
        game_schema: GameSchema  = GameSchema(schema_name=f"{self._game_id}.json")
        if self._game_id == "WAVES":
            game_extractor = WaveExtractor
        elif self._game_id == "CRYSTAL":
            game_extractor = CrystalExtractor
        elif self._game_id == "LAKELAND":
            game_extractor = LakelandExtractor
        elif self._game_id == "JOWILDER":
            game_extractor = JowilderExtractor
        elif self._game_id == "MAGNET":
            game_extractor = MagnetExtractor
        elif self._game_id in ["AQUALAB", "BACTERIA", "BALLOON", "CYCLE_CARBON", "CYCLE_NITROGEN", "CYCLE_WATER", "STEMPORTS", "EARTHQUAKE", "WIND"]:
            # all games with data but no extractor.
            pass
        else:
            raise Exception(f"Got an invalid game ID ({self._game_id})!")
        return game_schema, game_extractor

    def _extractToCSVs(self, request:Request, file_manager:FileManager, game_schema: GameSchema, table_schema: TableSchema, game_extractor: Union[type,None]):
        ret_val = -1
        try:
            sess_processor = evt_processor = None
            if request._files.sessions and game_extractor is not None:
                if game_extractor is not None:
                    sess_processor = SessionProcessor(ExtractorClass=game_extractor, table_schema=table_schema,
                                        game_schema=game_schema, sessions_csv_file=file_manager.GetSessionsFile())
                    sess_processor.WriteSessionCSVHeader()
                else:
                    utils.Logger.Log("Could not export sessions, no game extractor given!", logging.ERROR)
            if request._files.events:
                evt_processor = EventProcessor(table_schema=table_schema, game_schema=game_schema,
                                    events_csv_file=file_manager.GetEventsFile())
                evt_processor.WriteEventsCSVHeader()

            sess_ids = request.RetrieveSessionIDs()
            if sess_ids is None:
                sess_ids = []
            num_sess = len(sess_ids)
            utils.Logger.toStdOut(f"Preparing to process {num_sess} sessions.", logging.INFO)
            slice_size = self._settings["BATCH_SIZE"]
            session_slices = [[sess_ids[i] for i in
                            range( j*slice_size, min((j+1)*slice_size, num_sess) )] for j in
                            range( 0, math.ceil(num_sess / slice_size) )]
            for i, next_slice in enumerate(session_slices):
                start = datetime.now()
                next_data_set = request._interface.RowsFromIDs(next_slice)
                try:
                    # now, we process each row.
                    for row in next_data_set:
                        next_event = table_schema.RowToEvent(row)
                        #self._processRow(event=next_event, sess_ids=sess_ids, sess_processor=sess_processor, evt_processor=evt_processor)
                        if next_event.session_id in sess_ids:
                            # we check if there's an instance given, if not we obviously skip.
                            if sess_processor is not None:
                                sess_processor.ProcessRow(next_event)
                            if evt_processor is not None:
                                evt_processor.ProcessRow(row)
                        else:
                            utils.Logger.toFile(f"Found a session ({next_event.session_id}) which was in the slice but not in the list of sessions for processing.", logging.WARNING)
                    # after processing all rows for each slice, write out the session data and reset for next slice.
                    if request._files.sessions:
                        sess_processor.calculateAggregateFeatures()
                        sess_processor.WriteSessionCSVLines()
                        sess_processor.ClearLines()
                    if request._files.events:
                        evt_processor.WriteEventsCSVLines()
                        evt_processor.ClearLines()
                except Exception as err:
                    msg = f"Error while processing slice {i} of {len(session_slices)}"
                    raise err
                else:
                    time_delta = datetime.now() - start
                    num_min = math.floor(time_delta.total_seconds()/60)
                    num_sec = time_delta.total_seconds() % 60
                    num_events = len(next_data_set) if next_data_set is not None else 0
                    utils.Logger.Log(f"Processing time for slice [{i+1}/{len(session_slices)}]: {num_min} min, {num_sec:.3f} sec to handle {num_events} events", logging.INFO)
            ret_val = num_sess
        except Exception as err:
            msg = f"{type(err)} {str(err)}"
            utils.Logger.Log(msg, logging.ERROR)
            #traceback.print_tb(err.__traceback__)
            raise err
        finally:
            # Save out all the files.
            file_manager.CloseFiles()
            return ret_val
