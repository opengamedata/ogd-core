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
## import local files
import utils
from config import settings
from GameTable import GameTable
from managers.DataManager import *
from managers.FileManager import *
from managers.SessionProcessor import SessionProcessor
from managers.RawManager import RawManager
from managers.EventProcessor import EventProcessor
from Request import *
from schemas.Schema import Schema
from feature_extractors.WaveExtractor import WaveExtractor
from feature_extractors.CrystalExtractor import CrystalExtractor
from feature_extractors.LakelandExtractor import LakelandExtractor
from feature_extractors.JowilderExtractor import JowilderExtractor
from feature_extractors.MagnetExtractor import MagnetExtractor

## @class ExportManager
#  A class to export features and raw data, given a Request object.
class ExportManager:
    ## Constructor for the ExportManager class.
    #  Fairly simple, just saves some data for later use during export.
    #  @param game_id Initial id of game to export
    #                 (this can be changed, if a GameTable with a different id is
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

    ## Public function to use for feature extraction and csv export.
    #  Just sets up SQL-specific stuff, then defers to runExport to handle the rest.
    #  This call to runExport extracts features and exports raw and processed csv's based on the given request.
    #  @param request A data structure carrying parameters for feature extraction
    #                 and export.
    def ExportFromSQL(self, request: Request, game_schema: Schema):
        if request.game_id != self._game_id:
            utils.Logger.toFile(f"Changing ExportManager game from {self._game_id} to {request.game_id}", logging.WARNING)
            self._game_id = request.game_id
        # 1) we first get the source, which is a SQL connection.
        start = datetime.now()
        tunnel, db  = utils.SQL.prepareDB(db_settings=settings["db_config"], ssh_settings=settings["ssh_config"])
        if db is None:
            msg = f"Could not complete request {str(request)}, database connection failed."
            utils.Logger.Log(msg, logging.ERROR)
            utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)
            raise ConnectionError() # if we couldn't connect, we're DOA
        # If that was successful, we set up data retrieval with a game table and SQLDataManager.
        try:
            data_manager = SQLDataManager(game_id=request.game_id, game_schema=game_schema, settings=settings)
            date_range = (request.start_date, request.end_date)
            game_table: GameTable = GameTable.FromDB(db=db, settings=self._settings, request=request)

            #***
            time_delta = datetime.now() - start
            num_min = math.floor(time_delta.total_seconds()/60)
            num_sec = time_delta.total_seconds() % 60
            utils.Logger.Log(f"Database Connection Time: {num_min} min, {num_sec:.3f} sec", logging.INFO)
            # once we've set up DataManager and gotten a bit of data, we can run the Export.
            if self._runExport(data_manager=data_manager, date_range=date_range, game_table=game_table, export_files=request.export_files):
                utils.Logger.Log(f"Successfully completed request {str(request)}.", logging.INFO)
            else:
                utils.Logger.Log(f"Could not complete request {str(request)}", logging.ERROR)
        except Exception as err:
            msg = f"General error ExportFromSQL: {type(err)} {str(err)}"
            utils.SQL.server500Error(msg)
            utils.Logger.toFile(msg, logging.ERROR)
            traceback.print_tb(err.__traceback__)
        finally:
            utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)

    def ExtractFromFile(self, request: FileRequest, delimiter=','):
        if request.game_id != self._game_id:
            utils.Logger.toFile(f"Changing ExportManager game from {self._game_id} to {request.game_id}", logging.WARNING)
            self._game_id = request.game_id
        # 1) We first get the source, which is a file.
        try:
            zipped_file = zipfile.ZipFile(request.file_path)
            with zipped_file.open(zipped_file.namelist()[0]) as f:
                data_frame = pd.read_csv(filepath_or_buffer=f, delimiter=delimiter, parse_dates=['server_time', 'client_time'])
        except FileNotFoundError as err:
            msg = f"Could not complete request {str(request)}, failed to open {request.file_path}. {str(err)}"
            utils.Logger.toStdOut(msg, logging.ERROR)
            utils.Logger.toFile(msg, logging.ERROR)
            return
        # If that was successful, we then set up data retrieval with a game table and CSVDataManager.
        try:
            data_manager = CSVDataManager(game_id=data_frame['app_id'][0], data_frame=data_frame)
            date_range = (data_frame['server_time'].min(), data_frame['server_time'].max())
            game_table: GameTable = GameTable.FromCSV(data_frame=data_frame)
            # start = datetime.strptime(data_frame['server_time'].min().split(' ')[0], "%Y-%m-%d")
            # end = datetime.strptime(data_frame['server_time'].max().split(' ')[0], "%Y-%m-%d")
            # date_range = (start, end)
            # once we've set up DataManager and gotten a bit of data, we can run the Export.
            if self._runExport(data_manager=data_manager, date_range=date_range, game_table=game_table, export_files=request.export_files):
                utils.Logger.toStdOut(f"Successfully completed extraction from {request.file_path}.", logging.INFO)
            else:
                utils.Logger.toFile(f"Could not complete extraction from {request.file_path}", logging.ERROR)
        except Exception as err:
            msg = f"General error ExtractFromFile: {type(err)} {str(err)}"
            utils.SQL.server500Error(msg)
            utils.Logger.toFile(msg, logging.ERROR)
            traceback.print_tb(err.__traceback__)

    ## Private function containing most of the code to handle processing of db
    #  data, and export to files.
    #  @param request    A data structure carrying parameters for feature extraction
    #                    and export
    #  @param game_table A data structure containing information on how the db
    #                    table assiciated with the given game is structured. 
    def _runExport(self, data_manager: DataManager, date_range: typing.Tuple, game_table: GameTable, export_files: ExportFiles) -> bool:
        # utils.Logger.toStdOut(f"complex_data_index: {complex_data_index}", logging.DEBUG)
        try:
            # 2a) Prepare schema and extractor, if game doesn't have an extractor, make sure we don't try to export it.
            game_schema, game_extractor = self._prepareSchema()
            if game_extractor is None:
                export_files.sessions = False
            # 2b) Prepare files for export.
            file_manager = FileManager(export_files=export_files, game_id=self._game_id, \
                                       data_dir=self._settings["DATA_DIR"], date_range=date_range)
            file_manager.OpenFiles()
            # If we have a schema, we can do feature extraction.
            if game_schema is not None:
                # 4) Loop over data, running extractors.
                start = datetime.now()

                num_sess: int = self._extractToCSVs(file_manager=file_manager, data_manager=data_manager,\
                                    game_schema=game_schema, game_table=game_table, game_extractor=game_extractor, export_files=export_files)

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
                    utils.GenerateReadme(game_name=self._game_id, schema=game_schema, path=f"./data/{self._game_id}")
                file_manager.ZipFiles()
                # 6) Finally, update the list of csv files.
                file_manager.WriteMetadataFile(date_range=date_range, num_sess=num_sess)
                file_manager.UpdateFileExportList(date_range=date_range, num_sess=num_sess)
                ret_val = True
            else:
                ret_val = False
        except Exception as err:
            msg = f"{type(err)} {str(err)}"
            utils.Logger.toStdOut(msg, logging.ERROR)
            traceback.print_tb(err.__traceback__)
            utils.Logger.toFile(msg, logging.ERROR)
            ret_val = False
        finally:
            return ret_val

    def _prepareSchema(self):
        game_extractor: type = None
        game_schema: Schema  = Schema(schema_name=f"{self._game_id}.json")
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
        elif self._game_id in ["BACTERIA", "BALLOON", "CYCLE_CARBON", "CYCLE_NITROGEN", "CYCLE_WATER", "EARTHQUAKE", "WIND"]:
            # all games with data but no extractor.
            pass
        else:
            raise Exception(f"Got an invalid game ID ({self._game_id})!")
        return game_schema, game_extractor

    def _extractToCSVs(self, file_manager: FileManager, data_manager: DataManager,
                       game_schema: Schema, game_table: GameTable, game_extractor: type, export_files: ExportFiles):
        try:
            sess_processor = raw_mgr = evt_processor = None
            if export_files.sessions:
                sess_processor = SessionProcessor(ExtractorClass=game_extractor, game_table=game_table,
                                    game_schema=game_schema, sessions_csv_file=file_manager.GetSessionsFile())
                sess_processor.WriteSessionCSVHeader()
            if export_files.raw:
                raw_mgr = RawManager(game_table=game_table, game_schema=game_schema,
                                    raw_csv_file=file_manager.GetRawFile())
                raw_mgr.WriteRawCSVHeader()
            if export_files.events:
                evt_processor = EventProcessor(game_table=game_table, game_schema=game_schema,
                                    events_csv_file=file_manager.GetEventsFile())
                evt_processor.WriteEventsCSVHeader()

            num_sess = len(game_table.session_ids)
            utils.Logger.toStdOut(f"Preparing to process {num_sess} sessions.", logging.INFO)
            slice_size = self._settings["BATCH_SIZE"]
            session_slices = [[game_table.session_ids[i] for i in
                            range( j*slice_size, min((j+1)*slice_size, num_sess) )] for j in
                            range( 0, math.ceil(num_sess / slice_size) )]
            for i, next_slice in enumerate(session_slices):
                try:
                    start = datetime.now()
                    next_data_set = data_manager.RetrieveSliceData(next_slice)
                    # now, we process each row.
                    for row in next_data_set:
                        self._processRow(row=row, game_table=game_table, raw_mgr=raw_mgr, sess_processor=sess_processor, evt_processor=evt_processor)
                    # after processing all rows for each slice, write out the session data and reset for next slice.
                    if export_files.sessions:
                        sess_processor.calculateAggregateFeatures()
                        sess_processor.WriteSessionCSVLines()
                        sess_processor.ClearLines()
                    if export_files.raw:
                        raw_mgr.WriteRawCSVLines()
                        raw_mgr.ClearLines()
                    if export_files.events:
                        evt_processor.WriteEventsCSVLines()
                        evt_processor.ClearLines()
                except Exception as err:
                    raise Exception(f"Error while processing {next_data_set}, type={type(next_data_set)}")
                else:
                    time_delta = datetime.now() - start
                    num_min = math.floor(time_delta.total_seconds()/60)
                    num_sec = time_delta.total_seconds() % 60
                    num_events = len(next_data_set)
                    utils.Logger.Log(f"Processing time for slice [{i+1}/{len(session_slices)}]: {num_min} min, {num_sec:.3f} sec to handle {num_events} events", logging.INFO)
            ret_val = num_sess
        except Exception as err:
            msg = f"{type(err)} {str(err)}"
            utils.Logger.toStdOut(msg, logging.ERROR)
            traceback.print_tb(err.__traceback__)
            utils.Logger.toFile(msg, logging.ERROR)
            ret_val = -1
        finally:
            # Save out all the files.
            file_manager.CloseFiles()
            # if export_files.sessions:
            #     sessions_csv_file.close()
            # if export_files.raw:
            #     raw_csv_file.close()
            # if export_files.events:
            #     events_csv_file.close()
            return ret_val

    ## Private helper function to process a single row of data.
    #  Most of the processing is delegated to Events and Session Processors, but this
    #  function does a bit of pre-processing to parse the event_data_custom.
    #  @param row        The raw row data from a SQL query result.
    #  @param game_table A data structure containing information on how the db
    #                    table assiciated with the given game is structured. 
    #  @raw_mgr          An instance of RawManager used to track raw data.
    #  @sess_processor         An instance of SessionProcessor used to extract and track feature data.
    def _processRow(self, row: typing.Tuple, game_table: GameTable, raw_mgr: RawManager, sess_processor: SessionProcessor, evt_processor: EventProcessor):
        session_id = row[game_table.session_id_index]

        # parse out complex data from json
        col = row[game_table.complex_data_index]
        try:
            # complex_data_parsed = json.loads(col.replace("'", "\"")) if (col is not None) else {"event_custom":row[game_table.event_index]}
            complex_data_parsed = json.loads(col) if (col is not None) else {"event_custom":row[game_table.event_index]}
        except Exception as err:
            msg = f"When trying to parse {col}, get error\n{type(err)} {str(err)}"
            utils.Logger.toStdOut(msg, logging.ERROR)
            raise err

        # make sure we get *something* in the event_custom name
        # TODO: Make a better solution for games without event_custom fields in the logs themselves
        if self._game_id == 'LAKELAND' or self._game_id == 'JOWILDER':
            if type(complex_data_parsed) is not type({}):
                complex_data_parsed = {"item": complex_data_parsed}
            complex_data_parsed["event_custom"] = row[game_table.event_custom_index]
        elif "event_custom" not in complex_data_parsed.keys():
            complex_data_parsed["event_custom"] = row[game_table.event_index]
        # replace the json with parsed version.
        row = list(row)
        row[game_table.complex_data_index] = complex_data_parsed

        if session_id in game_table.session_ids:
            # we check if there's an instance given, if not we obviously skip.
            if sess_processor is not None:
                sess_processor.ProcessRow(row)
            if raw_mgr is not None:
                raw_mgr.ProcessRow(row)
            if evt_processor is not None:
                evt_processor.ProcessRow(row)
        # else:
            # in this case, we should have just found 
            # utils.Logger.toFile(f"Found a session ({session_id}) which was in the slice but not in the list of sessions for processing.", logging.WARNING)