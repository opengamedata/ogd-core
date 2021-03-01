import git
import json
import logging
import os
import re
import traceback
import typing
import zipfile
from datetime import datetime
## import local files
import utils
from Request import *

class FileManager(abc.ABC):
    def __init__(self, export_files: ExportFiles, game_id, data_dir: str, date_range: typing.Tuple):
        self._file_names : typing.Dict = {"sessions_f":None, "raw_f":None, "events_f":None}
        self._zip_names  : typing.Dict = {"sessions_f":None, "raw_f":None, "events_f":None}
        self._files      : typing.Dict = {"sessions_f":None, "raw_f":None, "events_f":None}
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
            self._file_names["sessions_f"] = base_path+"_session-features.csv" if export_files.sessions else None
            self._file_names["raw_f"]  = base_path+"_raw.tsv"  if export_files.raw  else None
            self._file_names["events_f"] = base_path+"_events.tsv" if export_files.events else None
            self._zip_names["sessions_f"] = base_path+"_session-features.zip" if export_files.sessions else None
            self._zip_names["raw_f"]  = base_path+"_raw.zip"  if export_files.raw  else None
            self._zip_names["events_f"] = base_path+"_events.zip" if export_files.events else None
        except Exception as err:
            msg = f"{type(err)} {str(err)}"
            utils.Logger.Log(msg, logging.ERROR)
            traceback.print_tb(err.__traceback__)

    def GetFiles(self):
        return self._files

    def GetSessionsFile(self):
        return self._files["sessions_f"]

    def GetRawFile(self):
        return self._files["raw_f"]

    def GetEventsFile(self):
        return self._files["events_f"]

    def OpenFiles(self):
        # Ensure we have a data directory.
        full_data_dir = self._data_dir + self._game_id
        os.makedirs(name=full_data_dir, exist_ok=True)
        # Then open up the files themselves.
        self._files["sessions_f"] = open(self._file_names["sessions_f"], "w", encoding="utf-8") if (self._file_names["sessions_f"] is not None) else None
        self._files["raw_f"]  = open(self._file_names["raw_f"] , "w", encoding="utf-8") if (self._file_names["raw_f"] is not None) else None
        self._files["events_f"] = open(self._file_names["events_f"], "w", encoding="utf-8") if (self._file_names["events_f"] is not None) else None

    def CloseFiles(self):
        if self._files["sessions_f"] is not None:
            self._files["sessions_f"].close()
        if self._files["raw_f"] is not None:
            self._files["raw_f"].close()
        if self._files["events_f"] is not None:
            self._files["events_f"].close()

    def ZipFiles(self):
        try:
            existing_csvs = utils.loadJSONFile("file_list.json", self._data_dir)
        except Exception as err:
            existing_csvs = {}
        # if we have already done this dataset before, rename old zip files
        # (of course, first check if we ever exported this game before).
        try:
            if (self._game_id in existing_csvs and self._dataset_id in existing_csvs[self._game_id]):
                src_sessions_f = existing_csvs[self._game_id][self._dataset_id]['sessions_f']
                src_raw_f  = existing_csvs[self._game_id][self._dataset_id]['raw_f']
                src_events_f = existing_csvs[self._game_id][self._dataset_id]['events_f']
                if src_sessions_f is not None:
                    os.rename(src_sessions_f, self._zip_names["sessions_f"])
                if src_raw_f is not None:
                    os.rename(src_raw_f, self._zip_names["raw_f"])
                if src_events_f is not None:
                    os.rename(src_events_f, self._zip_names["events_f"])
        except Exception as err:
            msg = f"Error while setting up zip files! {type(err)} : {err}"
            utils.Logger.Log(msg, logging.ERROR)
            traceback.print_tb(err.__traceback__)
        # for each file, try to save out the csv/tsv to a file - if it's one that should be exported, that is.
        base_path = f"{self._dataset_id}/{self._dataset_id}_{self._short_hash}"
        if self._files["sessions_f"] is not None:
            try:
                sessions_zip_file = zipfile.ZipFile(self._zip_names["sessions_f"], "w", compression=zipfile.ZIP_DEFLATED)
                self._addToZip(path=self._file_names["sessions_f"], zip_file=sessions_zip_file, path_in_zip=f"{base_path}_session-features.csv")
                self._addToZip(path=self._readme_path,        zip_file=sessions_zip_file, path_in_zip=f"{self._dataset_id}/readme.md")
                os.remove(self._file_names["sessions_f"])
            except FileNotFoundError as err:
                utils.Logger.Log(f"FileNotFoundError Exception: {err}", logging.ERROR)
                traceback.print_tb(err.__traceback__)
            finally:
                sessions_zip_file.close()
        if self._files["raw_f"] is not None:
            try:
                raw_zip_file = zipfile.ZipFile(self._zip_names["raw_f"], "w", compression=zipfile.ZIP_DEFLATED)
                self._addToZip(path=self._file_names["raw_f"], zip_file=raw_zip_file, path_in_zip=f"{base_path}_raw.tsv")
                self._addToZip(path=self._readme_path,       zip_file=raw_zip_file, path_in_zip=f"{self._dataset_id}/readme.md")
                os.remove(self._file_names["raw_f"])
            except FileNotFoundError as err:
                utils.Logger.Log(f"FileNotFoundError Exception: {err}", logging.ERROR)
                traceback.print_tb(err.__traceback__)
            finally:
                raw_zip_file.close()
        if self._files["events_f"] is not None:
            try:
                events_zip_file = zipfile.ZipFile(self._zip_names["events_f"], "w", compression=zipfile.ZIP_DEFLATED)
                self._addToZip(path=self._file_names["events_f"], zip_file=events_zip_file, path_in_zip=f"{base_path}_events.tsv")
                self._addToZip(path=self._readme_path,        zip_file=events_zip_file, path_in_zip=f"{self._dataset_id}/readme.md")
                os.remove(self._file_names["events_f"])
            except FileNotFoundError as err:
                utils.Logger.Log(f"FileNotFoundError Exception: {err}", logging.ERROR)
                traceback.print_tb(err.__traceback__)
            finally:
                events_zip_file.close()

    def _addToZip(self, path, zip_file, path_in_zip):
        try:
            zip_file.write(path, path_in_zip)
        except FileNotFoundError as err:
            utils.Logger.Log(str(err), logging.ERROR)
            traceback.print_tb(err.__traceback__)

    ## Public function to write out a tiny metadata file for indexing OGD data files.
    #  Using the paths of the exported files, and given some other variables for
    #  deriving file metadata, this simply outputs a new file_name.meta file.
    #  @param date_range    The range of dates included in the exported data.
    #  @param num_sess      The number of sessions included in the recent export.
    def WriteMetadataFile(self, date_range: typing.Tuple, num_sess: int):
        # First, ensure we have a data directory.
        try:
            full_data_dir = self._data_dir + self._game_id
            os.makedirs(name=full_data_dir, exist_ok=True)
        except Exception as err:
            msg = f"Could not set up folder {full_data_dir}. {type(err)} {str(err)}"
            utils.Logger.toFile(msg, logging.WARNING)
        else:
            # Second, remove old metas, if they exist.
            try:
                start_range = date_range[0].strftime("%Y%m%d")
                end_range = date_range[1].strftime("%Y%m%d")
                match_string = f"{self._game_id}_{start_range}_to_{end_range}_\\w*\\.meta"
                old_metas = [f for f in os.listdir(full_data_dir) if re.match(match_string, f)]
                for old_meta in old_metas:
                    utils.Logger.Log(f"Removing old meta file, {old_meta}")
                    os.remove(f"{full_data_dir}/{old_meta}")
            except Exception as err:
                msg = f"Could not remove old meta file {old_meta}. {type(err)} {str(err)}"
                utils.Logger.toFile(msg, logging.WARNING)
            # Third, write the new meta file.
            try:
                # calculate the path and name of the metadata file, and open/make it.
                meta_file_name = f"{full_data_dir}/{self._dataset_id}_{self._short_hash}.meta"
                meta_file = open(meta_file_name, "w", encoding="utf-8")
            except Exception as err:
                msg = f"Could not open file for metadata. {type(err)} {str(err)}"
                utils.Logger.toFile(msg, logging.WARNING)
            else:
                metadata  = \
                {
                    "game_id":self._game_id,
                    "dataset_id"   :self._dataset_id,
                    "sessions_f":self._zip_names["sessions_f"],
                    "raw_f" :self._zip_names["raw_f"],
                    "events_f":self._zip_names["events_f"],
                    "start_date"   :date_range[0].strftime("%m/%d/%Y"),
                    "end_date"     :date_range[1].strftime("%m/%d/%Y"),
                    "date_modified":datetime.now().strftime("%m/%d/%Y"),
                    "sessions":num_sess
                }
                meta_file.write(json.dumps(metadata, indent=4))
                meta_file.close()

    ## Public function to update the list of exported files.
    #  Using the paths of the exported files, and given some other variables for
    #  deriving file metadata, this simply updates the JSON file to the latest
    #  list of files.
    #  @param date_range    The range of dates included in the exported data.
    #  @param num_sess      The number of sessions included in the recent export.
    def UpdateFileExportList(self, date_range: typing.Tuple, num_sess: int):
        self._backupFileExportList()
        try:
            existing_csvs = utils.loadJSONFile("file_list.json", self._data_dir)
        except FileNotFoundError as err:
            utils.Logger.toFile("file_list.json does not exist.", logging.WARNING)
            existing_csvs = {}
        except Exception as err:
            msg = f"Could not load file list. {type(err)} {str(err)}"
            utils.Logger.toFile(msg, logging.ERROR)
            existing_csvs = {}
        finally:
            with open(f"{self._data_dir}file_list.json", "w") as existing_csv_file:
                utils.Logger.toStdOut(f"opened csv file at {existing_csv_file.name}", logging.INFO)
                if not self._game_id in existing_csvs.keys():
                    existing_csvs[self._game_id] = {}
                # raw_stat = os.stat(raw_csv_full_path)
                # sessions_stat = os.stat(sessions_csv_full_path)
                prior_export = self._dataset_id in existing_csvs[self._game_id].keys()
                sessions_path = self._zip_names["sessions_f"] if self._zip_names["sessions_f"] is not None else (existing_csvs[self._game_id][self._dataset_id]["sessions_f"] if prior_export else None)
                raw_path  = self._zip_names["raw_f"]  if self._zip_names["raw_f"]  is not None else (existing_csvs[self._game_id][self._dataset_id]["raw_f"]  if prior_export else None)
                events_path = self._zip_names["events_f"] if self._zip_names["events_f"] is not None else (existing_csvs[self._game_id][self._dataset_id]["events_f"] if prior_export else None)
                existing_csvs[self._game_id][self._dataset_id] = \
                {
                    "sessions_f":sessions_path,
                    "raw_f" :raw_path,
                    "events_f":events_path,
                    "start_date"   :date_range[0].strftime("%m/%d/%Y"),
                    "end_date"     :date_range[1].strftime("%m/%d/%Y"),
                    "date_modified":datetime.now().strftime("%m/%d/%Y"),
                    "sessions":num_sess
                }
                existing_csv_file.write(json.dumps(existing_csvs, indent=4))

    def _backupFileExportList(self) -> bool:
        try:
            existing_csvs = utils.loadJSONFile("file_list.json", self._data_dir) or {}
        except Exception as err:
            msg = f"{type(err)} {str(err)}"
            utils.Logger.toStdOut(f"Could not back up file_list.json. Got the following error: {msg}", logging.ERROR)
            utils.Logger.toFile(f"Could not back up file_list.json. Got the following error: {msg}", logging.ERROR)
            return False
        backup_csv_file = open(f"{self._data_dir}file_list.json.bak", "w")
        backup_csv_file.write(json.dumps(existing_csvs, indent=4))
        utils.Logger.toStdOut(f"Backed up file_list.json to {backup_csv_file.name}", logging.INFO)
        return True