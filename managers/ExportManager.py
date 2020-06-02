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
            game_table: GameTable = GameTable(db=db, settings=self._settings, request=request)
            try:
                parse_success: str = self._getAndParseData(request, game_table)
                if parse_success:
                    utils.Logger.toStdOut(f"Successfully completed request {str(request)}.", logging.INFO)
                else:
                    utils.Logger.toFile(f"Could not complete request {str(request)}", logging.ERROR)
            except Exception as err:
                utils.SQL.server500Error(str(err))
            finally:
                utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)

    ## Private function containing most of the code to handle processing of db
    #  data, and export to files.
    #  @param request    A data structure carrying parameters for feature extraction
    #                    and export
    #  @param game_table A data structure containing information on how the db
    #                    table assiciated with the given game is structured. 
    def _getAndParseData(self, request: Request, game_table: GameTable):
        data_directory = self._settings["DATA_DIR"] + self._game_id
        db_settings = self._settings["db_config"]
        
        # utils.Logger.toStdOut("complex_data_index: {}".format(complex_data_index), logging.DEBUG)

        # First, get the files and game-specific vars ready
        game_extractor: type
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
            game_schema = None
        else:
            raise Exception("Got an invalid game ID!")

        _from = request.start_date.strftime("%Y%m%d")
        _to = request.end_date.strftime("%Y%m%d")
        repo = git.Repo(search_parent_directories=True)
        short_hash = repo.git.rev_parse(repo.head.object.hexsha, short=7)
        dataset_id = f"{self._game_id}_{_from}_to_{_to}"

        try:
            existing_csvs = utils.loadJSONFile("file_list.json", self._settings['DATA_DIR'])

            os.makedirs(name=data_directory, exist_ok=True)
            readme_path:   str = f"{data_directory}/readme.md"
            raw_csv_path:  str = None
            proc_csv_path: str = None
            raw_zip_path:  str = None
            proc_zip_path: str = None
            num_sess:           int = len(game_table.session_ids)
            if game_schema is not None:
                raw_csv_path  = f"{data_directory}/{dataset_id}_{short_hash}_raw.tsv" # changed .csv to .tsv
                proc_csv_path = f"{data_directory}/{dataset_id}_{short_hash}_proc.csv"
                raw_zip_path  = f"{data_directory}/{dataset_id}_{short_hash}_raw.zip"
                proc_zip_path = f"{data_directory}/{dataset_id}_{short_hash}_proc.zip"
                if self._game_id in existing_csvs and dataset_id in existing_csvs[self._game_id]:
                    src_raw = existing_csvs[self._game_id][dataset_id]['raw']
                    src_proc = existing_csvs[self._game_id][dataset_id]['proc']
                    os.rename(src_raw, raw_zip_path)
                    os.rename(src_proc, proc_zip_path)
                self._extractToCSVs(raw_csv_path=raw_csv_path, proc_csv_path=proc_csv_path,\
                                    db_settings=db_settings,\
                                    game_schema=game_schema, game_table=game_table, game_extractor=game_extractor)
                raw_zip_file = zipfile.ZipFile(raw_zip_path, "w", compression=zipfile.ZIP_DEFLATED)
                proc_zip_file = zipfile.ZipFile(proc_zip_path, "w", compression=zipfile.ZIP_DEFLATED)
                self._addToZip(path=raw_csv_path, zip_file=raw_zip_file, path_in_zip=f"{dataset_id}/{dataset_id}_{short_hash}_raw.csv")
                self._addToZip(path=readme_path, zip_file=raw_zip_file, path_in_zip=f"{dataset_id}/readme.md")
                self._addToZip(path=proc_csv_path, zip_file=proc_zip_file, path_in_zip=f"{dataset_id}/{dataset_id}_{short_hash}_proc.csv")
                self._addToZip(path=readme_path, zip_file=proc_zip_file, path_in_zip=f"{dataset_id}/readme.md")
                raw_zip_file.close()
                proc_zip_file.close()
                os.remove(raw_csv_path)
                os.remove(proc_csv_path)
            # sql_dump_path = f"{data_directory}/{dataset_id}_{short_hash}.sql"
            sql_zip_path = None # f"{data_directory}/{dataset_id}_{short_hash}_sql.zip"
            if self._game_id in existing_csvs and dataset_id in existing_csvs[self._game_id]:
                src_sql = existing_csvs[self._game_id][dataset_id]['sql']
                os.rename(src_sql, sql_zip_path)
            # self._dumpToSQL(sql_dump_path=sql_dump_path, game_table=game_table, db_settings=db_settings, temp_table = f'{dataset_id}_{short_hash}')
            # sql_zip_file = zipfile.ZipFile(sql_zip_path, "w", compression=zipfile.ZIP_DEFLATED)
            # sql_zip_file.write(sql_dump_path, f"{dataset_id}/{dataset_id}_{short_hash}.sql")
            # sql_zip_file.write(readme_path, f"{dataset_id}/readme.md")
            # os.remove(sql_dump_path)
            # Finally, update the list of csv files.
            self._updateFileExportList(dataset_id, raw_zip_path, proc_zip_path,
                                    sql_zip_path, request, num_sess)
            ret_val = True
        except Exception as err:
            utils.Logger.toStdOut(str(err), logging.ERROR)
            traceback.print_tb(err.__traceback__)
            utils.Logger.toFile(str(err), logging.ERROR)
            ret_val = False
        finally:
            return ret_val

    def _addToZip(self, path, zip_file, path_in_zip):
        try:
            zip_file.write(path, path_in_zip)
        except FileNotFoundError as err:
            utils.Logger.toStdOut(str(err), logging.ERROR)
            traceback.print_tb(err.__traceback__)
            utils.Logger.toFile(str(err), logging.ERROR)

    def _extractToCSVs(self, raw_csv_path: str, proc_csv_path: str, db_settings,
                       game_schema: Schema, game_table: GameTable, game_extractor: type) -> int:
        try:
            tunnel, db  = utils.SQL.prepareDB(db_settings=settings["db_config"], ssh_settings=settings["ssh_config"])
            db_cursor = db.cursor()
            raw_csv_file = open(raw_csv_path, "w", encoding="utf-8")
            proc_csv_file = open(proc_csv_path, "w", encoding="utf-8")
            # Now, we're ready to set up the managers:
            raw_mgr = RawManager(game_table=game_table, game_schema=game_schema,
                                raw_csv_file=raw_csv_file)
            proc_mgr = ProcManager(ExtractorClass=game_extractor, game_table=game_table,
                                game_schema=game_schema, proc_csv_file=proc_csv_file)
            
            # We're moving the metadata out into a separate readme file.
            # # Next, calculate metadata
            # raw_metadata = utils.csvMetadata(game_name=self._game_id, begin_date=request.start_date, end_date=request.end_date,
            #                                 field_list=game_schema.db_columns_with_types())
            # feature_descriptions = {**game_schema.perlevel_features(), **game_schema.aggregate_features()}
            # proc_metadata = utils.csvMetadata(game_name=self._game_id, begin_date=request.start_date, end_date=request.end_date,
            #                                 field_list=feature_descriptions)
            # # after generating the metadata, write to each file
            # raw_csv_file.write(raw_metadata)
            # proc_csv_file.write(proc_metadata)

            # then write the column headers for the raw csv.
            raw_mgr.WriteRawCSVHeader()
            proc_mgr.WriteProcCSVHeader()

            num_sess = len(game_table.session_ids)
            utils.Logger.toStdOut(f"Preparing to process {num_sess} sessions.", logging.INFO)
            slice_size = self._settings["BATCH_SIZE"]
            session_slices = [[game_table.session_ids[i] for i in
                            range( j*slice_size, min((j+1)*slice_size, num_sess) )] for j in
                            range( 0, math.ceil(num_sess / slice_size) )]
            for next_slice in session_slices:
                # grab data for the given session range. Sort by event time, so
                select_query = self._select_query_from_slice(next_slice=next_slice, game_schema=game_schema)
                self._select_queries.append(select_query)
                next_data_set = utils.SQL.SELECTfromQuery(cursor=db_cursor, query=select_query, fetch_results=True)
                # now, we process each row.
                start = datetime.now()
                for row in next_data_set:
                    self._processRow(row, game_table, raw_mgr, proc_mgr)
                time_delta = datetime.now() - start
                num_min = math.floor(time_delta.total_seconds()/60)
                num_sec = time_delta.total_seconds() % 60
                num_events = len(next_data_set)
                utils.Logger.toStdOut(f"Slice processing time: {num_min} min, {num_sec:.3f} sec to handle {num_events} events", logging.INFO)
                utils.Logger.toFile(f"Slice processing time: {num_min} min, {num_sec:.3f} sec to handle {num_events} events", logging.INFO)
                
                # after processing all rows for all slices, write out the session data and reset for next slice.
                raw_mgr.WriteRawCSVLines()
                raw_mgr.ClearLines()
                proc_mgr.calculateAggregateFeatures()
                proc_mgr.WriteProcCSVLines()
                proc_mgr.ClearLines()
        except Exception as err:
            utils.Logger.toStdOut(str(err), logging.ERROR)
            traceback.print_tb(err.__traceback__)
            utils.Logger.toFile(str(err), logging.ERROR)
        finally:
            utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)
            return

    def _select_query_from_slice(self, next_slice: list, game_schema: Schema):
        if self._game_id == 'LAKELAND' or self._game_id == 'JOWILDER':
            ver_filter = f" AND app_version in ({','.join([str(x) for x in game_schema.schema()['config']['SUPPORTED_VERS']])}) "
        else:
            ver_filter = ''
        id_string = ','.join([f"'{x}'" for x in next_slice])
        # filt = f"app_id='{self._game_id}' AND (session_id  BETWEEN '{next_slice[0]}' AND '{next_slice[-1]}'){ver_filter}"
        filt = f"app_id='{self._game_id}' AND session_id  IN ({id_string}){ver_filter}"
        query = utils.SQL._prepareSelect(db_name=settings["db_config"]["DB_NAME_DATA"],
                                         table=settings["db_config"]["table"], columns=None, filter=filt, limit=-1,
                                         sort_columns=["session_id", "session_n"], sort_direction="ASC",
                                         grouping=None, distinct=False)
        return query

    def _dumpToSQL(self, sql_dump_path: str, game_table: GameTable, db_settings, temp_table: str):
        # args_list = ["mysqldump", f"--host={db_settings['DB_HOST']}",
        #             f"--where=", f"session_id BETWEEN '{game_table.session_ids[0]}' AND '{game_table.session_ids[-1]}'",
        #             f"--user={db_settings['DB_USER']}", f"--password={db_settings['DB_PW']}",
        #             f"{db_settings['DB_NAME_DATA']}", f"{db_settings['table']}"]
        if len(game_table.session_ids) > 0:
            db_name = db_settings["DB_NAME_DATA"]
            table = db_settings["table"]
            from_table_path = db_name + "." + str(table)
            to_table_path = db_name + "." + temp_table
            create_query = f'CREATE TABLE {to_table_path} LIKE {from_table_path};'
            get_insert_into_query = lambda select_query: f'INSERT INTO {to_table_path} '+select_query
            alter_query = f'ALTER TABLE {to_table_path} DROP COLUMN remote_addr;'
            drop_query = f'DROP TABLE {to_table_path};'
            try:
                tunnel, db  = utils.SQL.prepareDB(db_settings=settings["db_config"], ssh_settings=settings["ssh_config"])
                db_cursor = db.cursor()
                utils.SQL.Query(db_cursor, create_query)
                for select_query in self._select_queries:
                    insert_into_query = get_insert_into_query(select_query)
                    utils.SQL.Query(db_cursor, insert_into_query)
                utils.SQL.Query(db_cursor, alter_query)
#             command = f"mysqldump --host={db_settings['DB_HOST']} \
# --where=\"session_id BETWEEN '{game_table.session_ids[0]}' AND '{game_table.session_ids[-1]}' AND app_id='{self._game_id}'\" \
# --user={db_settings['DB_USER']} --password={db_settings['DB_PW']} {db_settings['DB_NAME_DATA']} {db_settings['table']} \
#  > {sql_dump_path}"
                command = f"mysqldump --host={db_settings['DB_HOST']} \
                --user={db_settings['DB_USER']} --password={db_settings['DB_PW']} {db_settings['DB_NAME_DATA']} {temp_table} \
                 > {sql_dump_path}"
                sql_dump_file = open(sql_dump_path, "w")
                utils.Logger.toStdOut(f"running sql dump command: {command}", logging.INFO)
                os.system(command)
                utils.SQL.Query(db_cursor, drop_query)
            except Exception as err:
                utils.Logger.toStdOut(str(err), logging.ERROR)
                traceback.print_tb(err.__traceback__)
                utils.Logger.toFile(str(err), logging.ERROR)
            finally:
                utils.SQL.disconnectMySQLViaSSH(tunnel=tunnel, db=db)
        else:
            utils.Logger.toStdOut(f"No sessions to export for {sql_dump_path}", logging.WARNING)
            utils.Logger.toFile(f"No sessions to export for {sql_dump_path}", logging.WARNING)


    ## Private helper function to process a single row of data.
    #  Most of the processing is delegated to Raw and Proc Managers, but this
    #  function does a bit of pre-processing to parse the event_data_custom.
    #  @param row        The raw row data from a SQL query result.
    #  @param game_table A data structure containing information on how the db
    #                    table assiciated with the given game is structured. 
    #  @raw_mgr          An instance of RawManager used to track raw data.
    #  @proc_mgr         An instance of ProcManager used to extract and track feature data.
    def _processRow(self, row: typing.Tuple, game_table: GameTable, raw_mgr: RawManager, proc_mgr: ProcManager):
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
            raw_mgr.ProcessRow(row)
            proc_mgr.ProcessRow(row)
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
    def _updateFileExportList(self, dataset_id: str, raw_csv_path: str, proc_csv_path: str,
        sql_dump_path: str, request: Request, num_sess: int):
        self._backupFileExportList()
        try:
            existing_csvs = utils.loadJSONFile("file_list.json", self._settings['DATA_DIR'])
        except Exception as err:
            existing_csvs = {}
        finally:
            existing_csv_file = open(f"{self._settings['DATA_DIR']}file_list.json", "w")
            utils.Logger.toStdOut(f"opened existing csv file at {existing_csv_file.name}", logging.INFO)
            if not self._game_id in existing_csvs:
                existing_csvs[self._game_id] = {}
            # raw_stat = os.stat(raw_csv_full_path)
            # proc_stat = os.stat(proc_csv_full_path)
            existing_csvs[self._game_id][dataset_id] = \
                {"raw":raw_csv_path,
                "proc":proc_csv_path,
                "sql":sql_dump_path,
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