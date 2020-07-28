## @package DataToCSV.py
#  A package to handle processing of stuff from our database,
#  for export to CSV files.

## import standard libraries
import git
import json
import logging
import math
import os
import subprocess
import traceback
import typing
import zipfile
from datetime import datetime
## import local files
import utils
from config import settings
from GameTable import GameTable
from managers.ProcManager import ProcManager
from managers.RawManager import RawManager
from managers.DumpManager import DumpManager
from Request import Request
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
        self._select_queries = []

    ## Public function to use for feature extraction and csv export.
    #  Extracts features and exports raw and processed csv's based on the given
    #  request.
    #  @param request A data structure carrying parameters for feature extraction
    #                 and export.
    def exportFromRequest(self, request: Request):
        if request.game_id != self._game_id:
            utils.Logger.toFile(f"Changing ExportManager game from {self._game_id} to {request.game_id}", logging.WARNING)
            self._game_id = request.game_id
        else:
            tunnel, db  = utils.SQL.prepareDB(db_settings=settings["db_config"], ssh_settings=settings["ssh_config"])
            game_table: GameTable = GameTable.FromDB(db=db, settings=self._settings, request=request)
            try:
                parse_success: bool = self._getAndParseData(request, game_table)
                if parse_success:
                    utils.Logger.toStdOut(f"Successfully completed request {str(request)}.", logging.INFO)
                else:
                    utils.Logger.toFile(f"Could not complete request {str(request)}", logging.ERROR)
            except Exception as err:
                utils.SQL.server500Error(str(err))
            finally:
                utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)

    def extractFromFile(self, file_path, delimiter=','):
        try:
            data = open(file=file_path, mode="r")
        except FileNotFoundError as err:
            utils.Logger.toStdOut(err, logging.ERROR)
            utils.Logger.toFile(err, logging.ERROR)
            return
        else:
            game_table = GameTable.fromFile(file_path, delimiter)


    ## Private function containing most of the code to handle processing of db
    #  data, and export to files.
    #  @param request    A data structure carrying parameters for feature extraction
    #                    and export
    #  @param game_table A data structure containing information on how the db
    #                    table assiciated with the given game is structured. 
    def _getAndParseData(self, request: Request, game_table: GameTable) -> bool:
        data_directory = self._settings["DATA_DIR"] + self._game_id
        db_settings = self._settings["db_config"]
        
        # utils.Logger.toStdOut("complex_data_index: {}".format(complex_data_index), logging.DEBUG)

        try:
            # TODO: get this pile of crap organized
            # First, get the files and game-specific vars ready
            game_schema, game_extractor = self._getExtractor()
            # also figure out hash and dataset ID.
            _from = request.start_date.strftime("%Y%m%d")
            _to = request.end_date.strftime("%Y%m%d")
            repo = git.Repo(search_parent_directories=True)
            short_hash = repo.git.rev_parse(repo.head.object.hexsha, short=7)
            dataset_id = f"{self._game_id}_{_from}_to_{_to}"

            # get the current list, and set up our paths.
            existing_csvs = utils.loadJSONFile("file_list.json", self._settings['DATA_DIR'])

            os.makedirs(name=data_directory, exist_ok=True)
            readme_path:   str = f"{data_directory}/readme.md"
            proc_csv_path: str = f"{data_directory}/{dataset_id}_{short_hash}_proc.csv"
            raw_csv_path:  str = f"{data_directory}/{dataset_id}_{short_hash}_raw.tsv" # changed .csv to .tsv
            dump_csv_path: str = f"{data_directory}/{dataset_id}_{short_hash}_dump.tsv"
            proc_zip_path: str = f"{data_directory}/{dataset_id}_{short_hash}_proc.zip"
            raw_zip_path:  str = f"{data_directory}/{dataset_id}_{short_hash}_raw.zip"
            dump_zip_path: str = f"{data_directory}/{dataset_id}_{short_hash}_dump.zip"
            num_sess:      int = len(game_table.session_ids)
            if game_schema is not None:
                self._extractToCSVs(raw_csv_path=raw_csv_path, proc_csv_path=proc_csv_path, dump_csv_path=dump_csv_path,\
                                    db_settings=db_settings,\
                                    game_schema=game_schema, game_table=game_table, game_extractor=game_extractor)
                if self._game_id in existing_csvs and dataset_id in existing_csvs[self._game_id]:
                    src_proc = existing_csvs[self._game_id][dataset_id]['proc']
                    src_raw = existing_csvs[self._game_id][dataset_id]['raw']
                    src_dump = existing_csvs[self._game_id][dataset_id]['dump']
                    os.rename(src_proc, proc_zip_path)
                    os.rename(src_raw, raw_zip_path)
                    os.rename(src_dump, dump_zip_path)
                try:
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

                try:
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

                try:
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
                                    dump_path=dump_zip_path, request=request, num_sess=num_sess)
            ret_val = True
        except Exception as err:
            utils.Logger.toStdOut(str(err), logging.ERROR)
            traceback.print_tb(err.__traceback__)
            utils.Logger.toFile(str(err), logging.ERROR)
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

    def _extractToCSVs(self, raw_csv_path: str, proc_csv_path: str, dump_csv_path: str,
                db_settings, game_schema: Schema, game_table: GameTable, game_extractor: type) -> int:
        try:
            tunnel, db  = utils.SQL.prepareDB(db_settings=settings["db_config"], ssh_settings=settings["ssh_config"])
            db_cursor = db.cursor()
            proc_csv_file = open(proc_csv_path, "w", encoding="utf-8")
            raw_csv_file = open(raw_csv_path, "w", encoding="utf-8")
            dump_csv_file = open(dump_csv_path, "w", encoding="utf-8")
            # Now, we're ready to set up the managers:
            proc_mgr = ProcManager(ExtractorClass=game_extractor, game_table=game_table,
                                game_schema=game_schema, proc_csv_file=proc_csv_file)
            raw_mgr = RawManager(game_table=game_table, game_schema=game_schema,
                                raw_csv_file=raw_csv_file)
            dump_mgr = DumpManager(game_table=game_table, game_schema=game_schema,
                                dump_csv_file=dump_csv_file)
            
            # then write the column headers for the raw csv.
            proc_mgr.WriteProcCSVHeader()
            raw_mgr.WriteRawCSVHeader()
            dump_mgr.WriteDumpCSVHeader()

            num_sess = len(game_table.session_ids)
            utils.Logger.toStdOut(f"Preparing to process {num_sess} sessions.", logging.INFO)
            slice_size = self._settings["BATCH_SIZE"]
            session_slices = [[game_table.session_ids[i] for i in
                            range( j*slice_size, min((j+1)*slice_size, num_sess) )] for j in
                            range( 0, math.ceil(num_sess / slice_size) )]
            for i, next_slice in enumerate(session_slices):
                # grab data for the given session range. Sort by event time, so
                select_query = self._selectQueryFromSlice(slice=next_slice, game_schema=game_schema)
                self._select_queries.append(select_query)
                next_data_set = utils.SQL.SELECTfromQuery(cursor=db_cursor, query=select_query, fetch_results=True)
                # now, we process each row.
                start = datetime.now()
                for row in next_data_set:
                    self._processRow(row=row, game_table=game_table, raw_mgr=raw_mgr, proc_mgr=proc_mgr, dump_mgr=dump_mgr)
                time_delta = datetime.now() - start
                num_min = math.floor(time_delta.total_seconds()/60)
                num_sec = time_delta.total_seconds() % 60
                num_events = len(next_data_set)

                status_string = f"Processing time for slice [{i+1}/{len(session_slices)}]: {num_min} min, {num_sec:.3f} sec to handle {num_events} events"
                utils.Logger.toStdOut(status_string, logging.INFO)
                utils.Logger.toFile(status_string, logging.INFO)
                
                # after processing all rows for all slices, write out the session data and reset for next slice.
                proc_mgr.calculateAggregateFeatures()
                proc_mgr.WriteProcCSVLines()
                proc_mgr.ClearLines()
                raw_mgr.WriteRawCSVLines()
                raw_mgr.ClearLines()
                dump_mgr.WriteDumpCSVLines()
                dump_mgr.ClearLines()
        except Exception as err:
            utils.Logger.toStdOut(str(err), logging.ERROR)
            traceback.print_tb(err.__traceback__)
            utils.Logger.toFile(str(err), logging.ERROR)
        finally:
            utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)
            return

    def _selectQueryFromSlice(self, slice: list, game_schema: Schema):
        if self._game_id == 'LAKELAND' or self._game_id == 'JOWILDER':
            ver_filter = f" AND app_version in ({','.join([str(x) for x in game_schema.schema()['config']['SUPPORTED_VERS']])}) "
        else:
            ver_filter = ''
        id_string = ','.join([f"'{x}'" for x in slice])
        # filt = f"app_id='{self._game_id}' AND (session_id  BETWEEN '{next_slice[0]}' AND '{next_slice[-1]}'){ver_filter}"
        filt = f"app_id='{self._game_id}' AND session_id  IN ({id_string}){ver_filter}"
        query = utils.SQL._prepareSelect(db_name=settings["db_config"]["DB_NAME_DATA"],
                                         table=settings["db_config"]["table"], columns=None, filter=filt, limit=-1,
                                         sort_columns=["session_id", "session_n"], sort_direction="ASC",
                                         grouping=None, distinct=False)
        return query

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
        complex_data_parsed = json.loads(col) if (col is not None) else {"event_custom":row[game_table.event_index]}
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
            proc_mgr.ProcessRow(row)
            raw_mgr.ProcessRow(row)
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
        dump_path: str, request: Request, num_sess: int):
        self._backupFileExportList()
        try:
            existing_csvs = utils.loadJSONFile("file_list.json", self._settings['DATA_DIR'])
        except Exception as err:
            utils.Logger.toFile(err, logging.WARNING)
            existing_csvs = {}
        finally:
            existing_csv_file = open(f"{self._settings['DATA_DIR']}file_list.json", "w")
            utils.Logger.toStdOut(f"opened existing csv file at {existing_csv_file.name}", logging.INFO)
            if not self._game_id in existing_csvs:
                existing_csvs[self._game_id] = {}
            # raw_stat = os.stat(raw_csv_full_path)
            # proc_stat = os.stat(proc_csv_full_path)
            existing_csvs[self._game_id][dataset_id] = \
                {"raw":raw_path,
                "proc":proc_path,
                "dump":dump_path,
                "start_date":request.start_date.strftime("%m/%d/%Y"),
                "end_date":request.end_date.strftime("%m/%d/%Y"),
                "date_modified":datetime.now().strftime("%m/%d/%Y"),
                "sessions":num_sess
                }
            existing_csv_file.write(json.dumps(existing_csvs, indent=4))

    def _backupFileExportList(self) -> bool:
        try:
            existing_csvs = utils.loadJSONFile("file_list.json", self._settings['DATA_DIR']) or {}
        except Exception as err:
            utils.Logger.toStdOut(f"Could not back up file_list.json. Got the following error: {str(err)}", logging.ERROR)
            utils.Logger.toFile(f"Could not back up file_list.json. Got the following error: {str(err)}", logging.ERROR)
            return False
        backup_csv_file = open(f"{self._settings['DATA_DIR']}file_list.json.bak", "w")
        backup_csv_file.write(json.dumps(existing_csvs, indent=4))
        utils.Logger.toStdOut(f"Backed up file_list.json to {backup_csv_file.name}", logging.INFO)
        return True