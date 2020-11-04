import traceback
import typing
## import local files
import utils
from Request import *

class FileManager(abc.ABC):
    def __init__(self, export_files: ExportFiles, game_id, data_dir: str, date_range: typing.Tuple):
        self._file_names : typing.Dict = {"proc":None, "raw":None, "dump":None}
        self._zip_names  : typing.Dict = {"proc":None, "raw":None, "dump":None}
        self._files      : typing.Dict = {"proc":None, "raw":None, "dump":None}
        self._data_dir   : str         = data_dir
        self._game_id    : str         = game_id
        self._readme_path: str
        self._dataset_id : str
        self._short_hash : str
        try:
            # figure out dataset ID.
            start = date_range[0].strftime("%Y%m%d")
            end = date_range[1].strftime("%Y%m%d")
            self._dataset_id = f"{self._game_id}_{start}_to_{end}"
            # get hash
            repo = git.Repo(search_parent_directories=True)
            self._short_hash = repo.git.rev_parse(repo.head.object.hexsha, short=7)
            # then set up our paths.
            full_data_dir = self._data_dir + game_id
            self._readme_path = f"{full_data_dir}/readme.md"
            base_path = f"{full_data_dir}/{self._dataset_id}_{self._short_hash}"
            # finally, generate file names.
            self._file_names["proc"] = base_path+"_proc.csv" if export_files.proc else None
            self._file_names["raw"]  = base_path+"_raw.tsv"  if export_files.raw  else None
            self._file_names["dump"] = base_path+"_dump.tsv" if export_files.dump else None
            self._zip_names["proc"] = base_path+"_proc.zip" if export_files.proc else None
            self._zip_names["raw"]  = base_path+"_raw.zip"  if export_files.raw  else None
            self._zip_names["dump"] = base_path+"_dump.zip" if export_files.dump else None
        except Exception as err:
            msg = f"{type(err)} {str(err)}"
            utils.Logger.Log(msg, logging.ERROR)
            traceback.print_tb(err.__traceback__)

    def GetFiles(self):
        return self._files

    def OpenFiles(self):
            # Ensure we have a data directory.
            full_data_dir = self._data_dir + self._game_id
            os.makedirs(name=full_data_dir, exist_ok=True)
            # Then open up the files themselves.
            self._files["proc"] = open(self._file_names["proc"], "w", encoding="utf-8") if export_files.proc else None
            self._files["raw"]  = open(self._file_names["raw"] , "w", encoding="utf-8") if export_files.raw else None
            self._files["dump"] = open(self._file_names["dump"], "w", encoding="utf-8") if export_files.dump else None

    def CloseFiles(self):
        if self._files["proc"] is not None:
            self._files["proc"].close()
        if self._files["raw"] is not None:
            self._files["raw"].close()
        if self._files["dump"] is not None:
            self._files["dump"].close()

    def ZipFiles(self):
        existing_csvs = utils.loadJSONFile("file_list.json", self._data_dir)
        # if we have already done this dataset before, rename old zip files
        # (of course, first check if we ever exported this game before).
        try:
            if (self._game_id in existing_csvs and self._dataset_id in existing_csvs[self._game_id]):
                src_proc = existing_csvs[self._game_id][dataset_id]['proc']
                src_raw  = existing_csvs[self._game_id][dataset_id]['raw']
                src_dump = existing_csvs[self._game_id][dataset_id]['dump']
                if src_proc is not None:
                    os.rename(src_proc, self._zip_names["proc"])
                if src_raw is not None:
                    os.rename(src_raw, self._zip_names["raw"])
                if src_dump is not None:
                    os.rename(src_dump, self._zip_names["dump"])
        except Exception as err:
            msg = f"Error while setting up zip files! {type(err)} : {err}"
            utils.Logger.Log(msg, logging.ERROR)
            traceback.print_tb(err.__traceback__)
        # for each file, try to save out the csv/tsv to a file - if it's one that should be exported, that is.
        base_path = f"{self._dataset_id}/{self._dataset_id}_{self._short_hash}"
        if self._files["proc"] is not None:
            try:
                proc_zip_file = zipfile.ZipFile(self._zip_names["proc"], "w", compression=zipfile.ZIP_DEFLATED)
                self._addToZip(path=self._file_names["proc"], zip_file=proc_zip_file, path_in_zip=f"{base_path}_proc.csv")
                self._addToZip(path=self._readme_path,        zip_file=proc_zip_file, path_in_zip=f"{self._dataset_id}/readme.md")
                os.remove(self._file_names["proc"])
            except FileNotFoundError as err:
                utils.Logger.Log(f"FileNotFoundError Exception: {err}", logging.ERROR)
                traceback.print_tb(err.__traceback__)
            finally:
                proc_zip_file.close()
        if self._files["raw"] is not None:
            try:
                raw_zip_file = zipfile.ZipFile(self._zip_names["raw"], "w", compression=zipfile.ZIP_DEFLATED)
                self._addToZip(path=self._file_names["raw"], zip_file=raw_zip_file, path_in_zip=f"{base_path}_raw.tsv")
                self._addToZip(path=self._readme_path,       zip_file=raw_zip_file, path_in_zip=f"{self._dataset_id}/readme.md")
                os.remove(self._file_names["raw"])
            except FileNotFoundError as err:
                utils.Logger.Log(f"FileNotFoundError Exception: {err}", logging.ERROR)
                traceback.print_tb(err.__traceback__)
            finally:
                raw_zip_file.close()
        if self._files["dump"] is not None:
            try:
                dump_zip_file = zipfile.ZipFile(self._zip_names["dump"], "w", compression=zipfile.ZIP_DEFLATED)
                self._addToZip(path=self._file_names["dump"], zip_file=dump_zip_file, path_in_zip=f"{base_path}_dump.tsv")
                self._addToZip(path=self._readme_path,        zip_file=dump_zip_file, path_in_zip=f"{self._dataset_id}/readme.md")
                os.remove(self._file_names["dump"])
            except FileNotFoundError as err:
                utils.Logger.Log(f"FileNotFoundError Exception: {err}", logging.ERROR)
                traceback.print_tb(err.__traceback__)
            finally:
                dump_zip_file.close()

    def _addToZip(self, path, zip_file, path_in_zip):
        try:
            zip_file.write(path, path_in_zip)
        except FileNotFoundError as err:
            utils.Logger.Log(str(err), logging.ERROR)
            traceback.print_tb(err.__traceback__)

    ## Public function to update the list of exported files.
    #  Given the paths of the exported files, and some other variables for
    #  deriving file metadata, this simply updates the JSON file to the latest
    #  list of files.
    #  @param dataset_id    The id used to identify a specific data set, based on
    #                       game id, and range of dates.
    #  @param raw_csv_path  Path to the newly exported raw csv, including filename
    #  @param proc_csv_path Path to the newly exported feature csv, including filename
    #  @param request       The original request for data export
    #  @param num_sess      The number of sessions included in the recent export.
    def UpdateFileExportList(self, date_range: typing.Tuple, num_sess: int):
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
            if not self._game_id in existing_csvs.keys():
                existing_csvs[self._game_id] = {}
            # raw_stat = os.stat(raw_csv_full_path)
            # proc_stat = os.stat(proc_csv_full_path)
            if dataset_id in existing_csvs[self._game_id].keys():
                proc_path = self._file_names["proc"] if self._file_names["proc"] is not None else existing_csvs[self._game_id][self._dataset_id]["proc"]
                raw_path  = self._file_names["raw"]  if self._file_names["raw"]  is not None else existing_csvs[self._game_id][self._dataset_id]["raw"]
                dump_path = self._file_names["dump"] if self._file_names["dump"] is not None else existing_csvs[self._game_id][self._dataset_id]["dump"]
            existing_csvs[self._game_id][dataset_id] = \
                {
                    "proc":proc_path,
                    "raw" :raw_path,
                    "dump":dump_path,
                    "start_date"   :date_range[0].strftime("%m/%d/%y"),
                    "end_date"     :date_range[1].strftime("%m/%d/%y"),
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