## @package DataToCSV.py
#  A package to handle processing of stuff from our database,
#  for export to CSV files.

## import standard libraries
import git
import json
import logging
import math
import logging
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
from managers.ProcManager import ProcManager
from managers.RawManager import RawManager
from managers.DumpManager import DumpManager
from Request import *
from schemas.Schema import Schema
from feature_extractors.WaveExtractor import WaveExtractor
from feature_extractors.CrystalExtractor import CrystalExtractor
from feature_extractors.LakelandExtractor import LakelandExtractor
from feature_extractors.JowilderExtractor import JowilderExtractor

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
    #  Extracts features and exports raw and processed csv's based on the given
    #  request.
    #  @param request A data structure carrying parameters for feature extraction
    #                 and export.
    def ExportFromSQL(self, request: Request, game_schema: Schema):
        if request.game_id != self._game_id:
            utils.Logger.toFile(f"Changing ExportManager game from {self._game_id} to {request.game_id}", logging.WARNING)
            self._game_id = request.game_id
        else:
            try:
                tunnel, db  = utils.SQL.prepareDB(db_settings=settings["db_config"], ssh_settings=settings["ssh_config"])
                if db is not None:
                    game_table: GameTable = GameTable.FromDB(db=db, settings=self._settings, request=request)
                    date_range = (request.start_date, request.end_date)
                    data_manager = SQLDataManager(game_id=request.game_id, game_schema=game_schema, settings=settings)
                    parse_success: bool = self._getAndParseData(data_manager=data_manager, date_range=date_range, game_table=game_table, export_files=request.export_files)
                    if parse_success:
                        utils.Logger.toStdOut(f"Successfully completed request {str(request)}.", logging.INFO)
                        utils.Logger.toFile(f"Successfully completed request {str(request)}.", logging.INFO)
                    else:
                        utils.Logger.toFile(f"Could not complete request {str(request)}", logging.ERROR)
                else:
                    utils.Logger.toFile(f"Could not complete request {str(request)}, database connection failed.", logging.ERROR)
            except Exception as err:
                msg = f"{type(err)} {str(err)}"
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
            utils.Logger.toStdOut(err, logging.ERROR)
            utils.Logger.toFile(err, logging.ERROR)
            return
        else:
            game_table = GameTable.FromCSV(data_frame=data_frame)
            try:
                data_manager = CSVDataManager(game_id=data_frame['app_id'][0], data_frame=data_frame)
                # start = datetime.strptime(data_frame['server_time'].min().split(' ')[0], "%Y-%m-%d")
                # end = datetime.strptime(data_frame['server_time'].max().split(' ')[0], "%Y-%m-%d")
                start = data_frame['server_time'].min()
                end = data_frame['server_time'].max()
                date_range = (start, end)
                parse_success: bool = self._getAndParseData(data_manager=data_manager, date_range=date_range, game_table=game_table, export_files=request.export_files)
                if parse_success:
                    utils.Logger.toStdOut(f"Successfully completed extraction from {request.file_path}.", logging.INFO)
                else:
                    utils.Logger.toFile(f"Could not complete extraction from {request.file_path}", logging.ERROR)
            except Exception as err:
                msg = f"{type(err)} {str(err)}"
                utils.SQL.server500Error(msg)
                utils.Logger.toFile(msg, logging.ERROR)
                traceback.print_tb(err.__traceback__)



    ## Private function containing most of the code to handle processing of db
    #  data, and export to files.
    #  @param request    A data structure carrying parameters for feature extraction
    #                    and export
    #  @param game_table A data structure containing information on how the db
    #                    table assiciated with the given game is structured. 
    def _getAndParseData(self, data_manager: DataManager, date_range: typing.Tuple, game_table: GameTable, export_files: ExportFiles) -> bool:
        data_directory = self._settings["DATA_DIR"] + self._game_id
        # db_settings = self._settings["db_config"]
        
        # utils.Logger.toStdOut("complex_data_index: {}".format(complex_data_index), logging.DEBUG)

        try:
            # TODO: get this pile of crap organized
            # First, get the files and game-specific vars ready
            game_schema, game_extractor = self._getExtractor()
            export_files.proc = export_files.proc and (game_extractor is not None) # if no game extractor, don't try to extract.
            # also figure out hash and dataset ID.
            _from = date_range[0].strftime("%Y%m%d")
            _to = date_range[1].strftime("%Y%m%d")
            repo = git.Repo(search_parent_directories=True)
            short_hash = repo.git.rev_parse(repo.head.object.hexsha, short=7)
            dataset_id = f"{self._game_id}_{_from}_to_{_to}"

            # get the current list, and set up our paths.
            existing_csvs = utils.loadJSONFile("file_list.json", self._settings['DATA_DIR'])
            os.makedirs(name=data_directory, exist_ok=True)
            readme_path:   str = f"{data_directory}/readme.md"
            proc_csv_path: str = f"{data_directory}/{dataset_id}_{short_hash}_proc.csv" if export_files.proc else None
            proc_zip_path: str = f"{data_directory}/{dataset_id}_{short_hash}_proc.zip" if export_files.proc else None
            raw_csv_path:  str = f"{data_directory}/{dataset_id}_{short_hash}_raw.tsv" if export_files.raw else None # changed .csv to .tsv
            raw_zip_path:  str = f"{data_directory}/{dataset_id}_{short_hash}_raw.zip" if export_files.raw else None
            dump_csv_path: str = f"{data_directory}/{dataset_id}_{short_hash}_dump.tsv" if export_files.dump else None
            dump_zip_path: str = f"{data_directory}/{dataset_id}_{short_hash}_dump.zip" if export_files.dump else None
            num_sess:      int = len(game_table.session_ids)
            # If we have a schema, we can do feature extraction.
            if game_schema is not None:
                # perform extraction
                self._extractToCSVs(raw_csv_path=raw_csv_path, proc_csv_path=proc_csv_path, dump_csv_path=dump_csv_path,\
                                    data_manager=data_manager,\
                                    game_schema=game_schema, game_table=game_table, game_extractor=game_extractor, export_files=export_files)
                # for each file, try to save out the csv/tsv to a file - if it's one that should be exported, that is.
                previously_exported = (self._game_id in existing_csvs and dataset_id in existing_csvs[self._game_id]) 
                if export_files.proc:
                    try:
                        # if we have already done this dataset before, rename old zip files
                        # (of course, first check if we ever exported this game before).
                        if previously_exported:
                            src_proc = existing_csvs[self._game_id][dataset_id]['proc']
                            if src_proc is not None:
                                os.rename(src_proc, proc_zip_path)
                        proc_zip_file = zipfile.ZipFile(proc_zip_path, "w", compression=zipfile.ZIP_DEFLATED)
                        self._addToZip(path=proc_csv_path, zip_file=proc_zip_file, path_in_zip=f"{dataset_id}/{dataset_id}_{short_hash}_proc.csv")
                        self._addToZip(path=readme_path, zip_file=proc_zip_file, path_in_zip=f"{dataset_id}/readme.md")
                        os.remove(proc_csv_path)
                    except FileNotFoundError as err:
                        utils.Logger.toStdOut(f"FileNotFoundError Exception: {err}", logging.ERROR)
                        traceback.print_tb(err.__traceback__)
                        utils.Logger.toFile(f"FileNotFoundError Exception: {err}", logging.ERROR)
                    finally:
                        proc_zip_file.close()
                if export_files.raw:
                    try:
                        # if we have already done this dataset before, rename old zip files
                        # (of course, first check if we ever exported this game before).
                        if previously_exported:
                            src_raw = existing_csvs[self._game_id][dataset_id]['raw']
                            if src_raw is not None:
                                os.rename(src_raw, raw_zip_path)
                        raw_zip_file = zipfile.ZipFile(raw_zip_path, "w", compression=zipfile.ZIP_DEFLATED)
                        self._addToZip(path=raw_csv_path, zip_file=raw_zip_file, path_in_zip=f"{dataset_id}/{dataset_id}_{short_hash}_raw.tsv")
                        self._addToZip(path=readme_path, zip_file=raw_zip_file, path_in_zip=f"{dataset_id}/readme.md")
                        os.remove(raw_csv_path)
                    except FileNotFoundError as err:
                        utils.Logger.toStdOut(f"FileNotFoundError Exception: {err}", logging.ERROR)
                        traceback.print_tb(err.__traceback__)
                        utils.Logger.toFile(f"FileNotFoundError Exception: {err}", logging.ERROR)
                    finally:
                        raw_zip_file.close()
                if export_files.dump:
                    try:
                        # if we have already done this dataset before, rename old zip files
                        # (of course, first check if we ever exported this game before).
                        if previously_exported:
                            src_dump = existing_csvs[self._game_id][dataset_id]['dump']
                            if src_dump is not None:
                                os.rename(src_dump, dump_zip_path)
                        dump_zip_file = zipfile.ZipFile(dump_zip_path, "w", compression=zipfile.ZIP_DEFLATED)
                        self._addToZip(path=dump_csv_path, zip_file=dump_zip_file, path_in_zip=f"{dataset_id}/{dataset_id}_{short_hash}_dump.tsv")
                        self._addToZip(path=readme_path, zip_file=dump_zip_file, path_in_zip=f"{dataset_id}/readme.md")
                        os.remove(dump_csv_path)
                    except FileNotFoundError as err:
                        utils.Logger.toStdOut(f"FileNotFoundError Exception: {err}", logging.ERROR)
                        traceback.print_tb(err.__traceback__)
                        utils.Logger.toFile(f"FileNotFoundError Exception: {err}", logging.ERROR)
                    finally:
                        dump_zip_file.close()
            # Finally, update the list of csv files.
            self._updateFileExportList(dataset_id=dataset_id, raw_path=raw_zip_path, proc_path=proc_zip_path,
                                    dump_path=dump_zip_path, date_range=date_range, num_sess=num_sess)
            ret_val = True
        except Exception as err:
            msg = f"{type(err)} {str(err)}"
            utils.Logger.toStdOut(msg, logging.ERROR)
            traceback.print_tb(err.__traceback__)
            utils.Logger.toFile(msg, logging.ERROR)
            ret_val = False
        finally:
            return ret_val

    def _getExtractor(self):
        game_extractor: type = None
        game_schema: Schema = None
        if self._game_id == "WAVES":
            game_schema = Schema(schema_name="WAVES.json")
            game_extractor = WaveExtractor
        elif self._game_id == "CRYSTAL":
            game_schema = Schema(schema_name="CRYSTAL.json")
            game_extractor = CrystalExtractor
        elif self._game_id == "LAKELAND":
            game_schema = Schema(schema_name="LAKELAND.json")
            game_extractor = LakelandExtractor
        elif self._game_id == "JOWILDER":
            game_schema = Schema(schema_name="JOWILDER.json")
            game_extractor = JowilderExtractor
        elif self._game_id in ["BACTERIA", "BALLOON", "CYCLE_CARBON", "CYCLE_NITROGEN", "CYCLE_WATER", "EARTHQUAKE", "MAGNET", "WIND"]:
            # all games with data but no extractor.
            pass
        else:
            raise Exception("Got an invalid game ID!")
        return game_schema, game_extractor

    def _addToZip(self, path, zip_file, path_in_zip):
        try:
            zip_file.write(path, path_in_zip)
        except FileNotFoundError as err:
            utils.Logger.toStdOut(str(err), logging.ERROR)
            traceback.print_tb(err.__traceback__)
            utils.Logger.toFile(str(err), logging.ERROR)

    def _extractToCSVs(self, raw_csv_path: str, proc_csv_path: str, dump_csv_path: str, data_manager: DataManager,
                       game_schema: Schema, game_table: GameTable, game_extractor: type, export_files: ExportFiles):
        try:
            proc_mgr = raw_mgr = dump_mgr = None
            if export_files.proc:
                proc_csv_file = open(proc_csv_path, "w", encoding="utf-8")
                proc_mgr = ProcManager(ExtractorClass=game_extractor, game_table=game_table,
                                    game_schema=game_schema, proc_csv_file=proc_csv_file)
                proc_mgr.WriteProcCSVHeader()
            if export_files.raw:
                raw_csv_file = open(raw_csv_path, "w", encoding="utf-8")
                raw_mgr = RawManager(game_table=game_table, game_schema=game_schema,
                                    raw_csv_file=raw_csv_file)
                raw_mgr.WriteRawCSVHeader()
            if export_files.dump:
                dump_csv_file = open(dump_csv_path, "w", encoding="utf-8")
                dump_mgr = DumpManager(game_table=game_table, game_schema=game_schema,
                                    dump_csv_file=dump_csv_file)
                dump_mgr.WriteDumpCSVHeader()

            num_sess = len(game_table.session_ids)
            utils.Logger.toStdOut(f"Preparing to process {num_sess} sessions.", logging.INFO)
            slice_size = self._settings["BATCH_SIZE"]
            session_slices = [[game_table.session_ids[i] for i in
                            range( j*slice_size, min((j+1)*slice_size, num_sess) )] for j in
                            range( 0, math.ceil(num_sess / slice_size) )]
            for i, next_slice in enumerate(session_slices):
                next_data_set = data_manager.RetrieveSliceData(next_slice)
                # now, we process each row.
                start = datetime.now()
                for row in next_data_set:
                    self._processRow(row=row, game_table=game_table, raw_mgr=raw_mgr, proc_mgr=proc_mgr, dump_mgr=dump_mgr)
                time_delta = datetime.now() - start
                num_min = math.floor(time_delta.total_seconds()/60)
                num_sec = time_delta.total_seconds() % 60
                try:
                    num_events = len(next_data_set)
                except Exception as err:
                    raise Exception(f"Error while processing {next_data_set}, type={type(next_data_set)}")

                status_string = f"Processing time for slice [{i+1}/{len(session_slices)}]: {num_min} min, {num_sec:.3f} sec to handle {num_events} events"
                utils.Logger.toStdOut(status_string, logging.INFO)
                utils.Logger.toFile(status_string, logging.INFO)
                
                # after processing all rows for all slices, write out the session data and reset for next slice.
                if export_files.proc:
                    proc_mgr.calculateAggregateFeatures()
                    proc_mgr.WriteProcCSVLines()
                    proc_mgr.ClearLines()
                if export_files.raw:
                    raw_mgr.WriteRawCSVLines()
                    raw_mgr.ClearLines()
                if export_files.dump:
                    dump_mgr.WriteDumpCSVLines()
                    dump_mgr.ClearLines()
        except Exception as err:
            msg = f"{type(err)} {str(err)}"
            utils.Logger.toStdOut(msg, logging.ERROR)
            traceback.print_tb(err.__traceback__)
            utils.Logger.toFile(msg, logging.ERROR)
        finally:
            if export_files.proc:
                proc_csv_file.close()
            if export_files.raw:
                raw_csv_file.close()
            if export_files.dump:
                dump_csv_file.close()
            return

    ## Private helper function to process a single row of data.
    #  Most of the processing is delegated to Raw and Proc Managers, but this
    #  function does a bit of pre-processing to parse the event_data_custom.
    #  @param row        The raw row data from a SQL query result.
    #  @param game_table A data structure containing information on how the db
    #                    table assiciated with the given game is structured. 
    #  @raw_mgr          An instance of RawManager used to track raw data.
    #  @proc_mgr         An instance of ProcManager used to extract and track feature data.
    def _processRow(self, row: typing.Tuple, game_table: GameTable, raw_mgr: RawManager, proc_mgr: ProcManager, dump_mgr: DumpManager):
        session_id = row[game_table.session_id_index]

        # parse out complex data from json
        col = row[game_table.complex_data_index]
        try:
            complex_data_parsed = json.loads(col.replace("'", "\"")) if (col is not None) else {"event_custom":row[game_table.event_index]}
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
            if proc_mgr is not None:
                proc_mgr.ProcessRow(row)
            if raw_mgr is not None:
                raw_mgr.ProcessRow(row)
            if dump_mgr is not None:
                dump_mgr.ProcessRow(row)
        # else:
            # in this case, we should have just found 
            # utils.Logger.toFile(f"Found a session ({session_id}) which was in the slice but not in the list of sessions for processing.", logging.WARNING)

    ## Private helper function to update the list of exported files.
    #  Given the paths of the exported files, and some other variables for
    #  deriving file metadata, this simply updates the JSON file to the latest
    #  list of files.
    #  @param dataset_id    The id used to identify a specific data set, based on
    #                       game id, and range of dates.
    #  @param raw_csv_path  Path to the newly exported raw csv, including filename
    #  @param proc_csv_path Path to the newly exported feature csv, including filename
    #  @param request       The original request for data export
    #  @param num_sess      The number of sessions included in the recent export.
    def _updateFileExportList(self, dataset_id: str, raw_path: str, proc_path: str,
        dump_path: str, date_range: typing.Tuple, num_sess: int):
        self._backupFileExportList()
        try:
            existing_csvs = utils.loadJSONFile("file_list.json", self._settings['DATA_DIR'])
        except Exception as err:
            msg = f"{type(err)} {str(err)}"
            utils.Logger.toFile(msg, logging.WARNING)
            existing_csvs = {}
        finally:
            existing_csv_file = open(f"{self._settings['DATA_DIR']}file_list.json", "w")
            utils.Logger.toStdOut(f"opened existing csv file at {existing_csv_file.name}", logging.INFO)
            if not self._game_id in existing_csvs:
                existing_csvs[self._game_id] = {}
            # raw_stat = os.stat(raw_csv_full_path)
            # proc_stat = os.stat(proc_csv_full_path)
            if self._game_id in existing_csvs.keys() and dataset_id in existing_csvs[self._game_id].keys():
                proc_path = proc_path if proc_path is not None else existing_csvs[self._game_id][dataset_id]["proc"]
                raw_path = raw_path if raw_path is not None else existing_csvs[self._game_id][dataset_id]["raw"]
                dump_path = dump_path if dump_path is not None else existing_csvs[self._game_id][dataset_id]["dump"]
            existing_csvs[self._game_id][dataset_id] = \
                {"raw":raw_path,
                "proc":proc_path,
                "dump":dump_path,
                "start_date":date_range[0].strftime("%m/%d/%y"),
                "end_date":date_range[1].strftime("%m/%d/%y"),
                "date_modified":datetime.now().strftime("%m/%d/%Y"),
                "sessions":num_sess
                }
            existing_csv_file.write(json.dumps(existing_csvs, indent=4))

    def _backupFileExportList(self) -> bool:
        try:
            existing_csvs = utils.loadJSONFile("file_list.json", self._settings['DATA_DIR']) or {}
        except Exception as err:
            msg = f"{type(err)} {str(err)}"
            utils.Logger.toStdOut(f"Could not back up file_list.json. Got the following error: {msg}", logging.ERROR)
            utils.Logger.toFile(f"Could not back up file_list.json. Got the following error: {msg}", logging.ERROR)
            return False
        backup_csv_file = open(f"{self._settings['DATA_DIR']}file_list.json.bak", "w")
        backup_csv_file.write(json.dumps(existing_csvs, indent=4))
        utils.Logger.toStdOut(f"Backed up file_list.json to {backup_csv_file.name}", logging.INFO)
        return True