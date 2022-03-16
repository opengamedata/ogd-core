# global imports
import abc
import git
import json
import logging
import os
import re
import shutil
import sys
import traceback
import zipfile
from datetime import datetime
from git.exc import InvalidGitRepositoryError, NoSuchPathError
from pathlib import Path
from typing import Any, Dict, IO, Union

## local imports
import utils
from schemas.GameSchema import GameSchema
from schemas.TableSchema import TableSchema
from schemas.Request import Request

class FileManager(abc.ABC):
    @staticmethod
    def GenerateReadme(game_schema:GameSchema, table_schema:TableSchema, path:Path = Path("./")):
        try:
            os.makedirs(name=path, exist_ok=True)
            with open(path / "readme.md", "w") as readme:
                # 1. Open files with game-specific readme data, and global db changelog.
                source_dir = Path("./doc/readme_src/")
                try:
                    with open(source_dir / f"{game_schema._game_name}_readme_src.md", "r") as readme_src:
                        readme.write(readme_src.read())
                except FileNotFoundError as err:
                    readme.write("No game readme prepared")
                    utils.Logger.Log(f"Could not find {game_schema._game_name}_readme_src", logging.WARNING)
                finally:
                    readme.write("\n\n")
                # 2. Use schema to write feature & column descriptions to the readme.
                meta = FileManager.GenCSVMetadata(game_schema=game_schema, table_schema=table_schema)
                readme.write(meta)
                # 3. Append any important data from the data changelog.
                try:
                    with open(source_dir / "changelog_src.md", "r") as changelog_src:
                        readme.write(changelog_src.read())
                except FileNotFoundError as err:
                    readme.write("No changelog prepared")
                    utils.Logger.Log(f"Could not find changelog_src", logging.WARNING)
        except FileNotFoundError as err:
            utils.Logger.Log(f"Could not open readme.md for writing.", logging.ERROR)
            traceback.print_tb(err.__traceback__)

    @staticmethod
    def GenCSVMetadata(game_schema: GameSchema, table_schema: TableSchema) -> str:
        """Function to generate markdown-formatted metadata for a given game.
        Gives a summary of the data licensing and suggested citation,
        then adds the markdown-formatted information from game and table schemas.

        :param game_schema: [description]
        :type game_schema: GameSchema
        :param table_schema: [description]
        :type table_schema: TableSchema
        :return: A string containing metadata for the given game.
        :rtype: str
        """
        template_str =\
        "\n".join(["## Field Day Open Game Data  ",
        "### Retrieved from https://fielddaylab.wisc.edu/opengamedata  ",
        "### These anonymous data are provided in service of future educational data mining research.  ",
        "### They are made available under the Creative Commons CCO 1.0 Universal license.  ",
        "### See https://creativecommons.org/publicdomain/zero/1.0/  ",
        "",
        "## Suggested citation:  ",
        "### Field Day. (2019). Open Educational Game Play Logs - [dataset ID]. Retrieved [today's date] from https://fielddaylab.wisc.edu/opengamedata  ",
        "",
        f"# Game: {game_schema._game_name}  ",
        "",
        "## Field Descriptions:  \n",
        f"{table_schema.Markdown()}",
        "",
        f"{game_schema.Markdown()}",
        ""])
        return template_str

    def __init__(self, request:Request, data_dir:str, extension:str="tsv"):
        self._file_names   : Dict[str,Union[Path,None]] = {"population":None, "players":None, "sessions":None, "events":None}
        self._zip_names    : Dict[str,Union[Path,None]] = {"population":None, "players":None, "sessions":None, "events":None}
        self._files        : Dict[str,Union[IO,None]]   = {"population":None, "players":None, "sessions":None, "events":None}
        self._game_id      : str  = request.GetGameID()
        self._data_dir     : Path = Path("./" + data_dir)
        self._game_data_dir: Path = self._data_dir / self._game_id
        self._readme_path  : Path = self._game_data_dir/ "readme.md"
        self._extension    : str  = extension
        self._date_range   : Dict[str,Union[datetime,None]] = request.GetRange().GetDateRange()
        self._dataset_id   : str  = ""
        self._short_hash   : str  = ""
        # figure out dataset ID.
        start = self._date_range['min'].strftime("%Y%m%d") if self._date_range['min'] is not None else "UNKNOWN"
        end   = self._date_range['max'].strftime("%Y%m%d") if self._date_range['max'] is not None else "UNKNOWN"
        self._dataset_id = f"{self._game_id}_{start}_to_{end}"
        # get hash
        try:
            repo = git.Repo(search_parent_directories=True)
            if repo.git is not None:
                self._short_hash = str(repo.git.rev_parse(repo.head.object.hexsha, short=7))
        except InvalidGitRepositoryError as err:
            msg = f"Code is not in a valid Git repository:\n{str(err)}"
            utils.Logger.Log(msg, logging.ERROR)
        except NoSuchPathError as err:
            msg = f"Unable to access proper file paths for Git repository:\n{str(err)}"
            utils.Logger.Log(msg, logging.ERROR)
        # then set up our paths, and ensure each exists.
        base_file_name    : str  = f"{self._dataset_id}_{self._short_hash}"
        # finally, generate file names.
        if request.ExportEvents():
            self._file_names['events']     = self._game_data_dir / f"{base_file_name}_events.{self._extension}"
            self._zip_names['events']      = self._game_data_dir / f"{base_file_name}_events.zip"
        if request.ExportSessions():
            self._file_names['sessions']   = self._game_data_dir / f"{base_file_name}_session-features.{self._extension}"
            self._zip_names['sessions']    = self._game_data_dir / f"{base_file_name}_session-features.zip"
        if request.ExportPlayers():
            self._file_names['players']   = self._game_data_dir / f"{base_file_name}_player-features.{self._extension}"
            self._zip_names['players']    = self._game_data_dir / f"{base_file_name}_player-features.zip"
        if request.ExportPopulation():
            self._file_names['population'] = self._game_data_dir / f"{base_file_name}_population-features.{self._extension}"
            self._zip_names['population']  = self._game_data_dir / f"{base_file_name}_population-features.zip"

    def GetFiles(self) -> Dict[str,Union[IO,None]]:
        return self._files

    def GetPopulationFile(self) -> IO:
        ret_val : IO = sys.stdout
        if self._files['population'] is not None:
            ret_val = self._files['population']
        else:
            utils.Logger.Log("No population file available, returning standard output instead.", logging.WARN)
        return ret_val

    def GetPlayersFile(self) -> IO:
        ret_val : IO = sys.stdout
        if self._files['players'] is not None:
            ret_val = self._files['players']
        else:
            utils.Logger.Log("No player file available, returning standard output instead.", logging.WARN)
        return ret_val

    def GetSessionsFile(self) -> IO:
        ret_val : IO = sys.stdout
        if self._files['sessions'] is not None:
            ret_val = self._files['sessions']
        else:
            utils.Logger.Log("No sessions file available, returning standard output instead.", logging.WARN)
        return ret_val

    def GetEventsFile(self) -> IO:
        ret_val : IO = sys.stdout
        if self._files['events'] is not None:
            ret_val = self._files['events']
        else:
            utils.Logger.Log("No events file available, returning standard output instead.", logging.WARN)
        return ret_val

    def WritePopulationFile(self, data:str) -> None:
        if self._files['population'] is not None:
            self._files['population'].write(data)
        else:
            utils.Logger.Log("No population file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write(data)

    def WritePlayersFile(self, data:str) -> None:
        if self._files['players'] is not None:
            self._files['players'].write(data)
        else:
            utils.Logger.Log("No player file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write(data)

    def WriteSessionsFile(self, data:str) -> None:
        if self._files['sessions'] is not None:
            self._files['sessions'].write(data)
        else:
            utils.Logger.Log("No sessions file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write(data)

    def WriteEventsFile(self, data:str) -> None:
        if self._files['events'] is not None:
            self._files['events'].write(data)
        else:
            utils.Logger.Log("No events file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write(data)

    def OpenFiles(self) -> None:
        # self._data_dir.mkdir(exist_ok=True)
        self._game_data_dir.mkdir(exist_ok=True, parents=True)
        # self._base_path.mkdir(exist_ok=True)
        self._files['population'] = open(self._file_names['population'], "w+", encoding="utf-8") if (self._file_names['population'] is not None) else None
        self._files['players']  = open(self._file_names['players'],  "w+", encoding="utf-8") if (self._file_names['players'] is not None) else None
        self._files['sessions'] = open(self._file_names['sessions'], "w+", encoding="utf-8") if (self._file_names['sessions'] is not None) else None
        self._files['events']   = open(self._file_names['events'],   "w+", encoding="utf-8") if (self._file_names['events'] is not None) else None

    def CloseFiles(self) -> None:
        if self._files['population'] is not None:
            self._files['population'].close()
        if self._files['players'] is not None:
            self._files['players'].close()
        if self._files['sessions'] is not None:
            self._files['sessions'].close()
        if self._files['events'] is not None:
            self._files['events'].close()

    def ZipFiles(self) -> None:
        try:
            existing_csvs = utils.loadJSONFile(filename="file_list.json", path=self._data_dir)
        except Exception as err:
            existing_csvs = {}
        # if we have already done this dataset before, rename old zip files
        # (of course, first check if we ever exported this game before).
        if (self._game_id in existing_csvs and self._dataset_id in existing_csvs[self._game_id]):
            existing_data = existing_csvs[self._game_id][self._dataset_id]
            _existing_pop_file     = existing_data.get('population_file', None)
            _existing_players_file = existing_data.get('players_file', None)
            _existing_sess_file    = existing_data.get('sessions_file', None)
            _existing_events_file  = existing_data.get('events_file', None)
            try:
                if _existing_pop_file is not None and self._zip_names['population'] is not None:
                    utils.Logger.Log(f"Renaming {str(_existing_pop_file)} -> {self._zip_names['population']}", logging.DEBUG)
                    os.rename(_existing_pop_file, str(self._zip_names['population']))
                if _existing_players_file is not None and self._zip_names['players'] is not None:
                    os.rename(_existing_players_file, str(self._zip_names['players']))
                if _existing_sess_file is not None and self._zip_names['sessions'] is not None:
                    os.rename(_existing_sess_file, str(self._zip_names['sessions']))
                if _existing_events_file is not None and self._zip_names['events'] is not None:
                    os.rename(_existing_events_file, str(self._zip_names['events']))
            except Exception as err:
                msg = f"Error while setting up zip files! {type(err)} : {err}"
                utils.Logger.Log(msg, logging.ERROR)
                traceback.print_tb(err.__traceback__)
        # for each file, try to save out the csv/tsv to a file - if it's one that should be exported, that is.
        if self._zip_names['population'] is not None:
            with zipfile.ZipFile(self._zip_names["population"], "w", compression=zipfile.ZIP_DEFLATED) as population_zip_file:
                try:
                    population_file = Path(self._dataset_id) / f"{self._dataset_id}_{self._short_hash}_population-features.{self._extension}"
                    readme_file  = Path(self._dataset_id) / "readme.md"
                    self._addToZip(path=self._file_names["population"], zip_file=population_zip_file, path_in_zip=population_file)
                    self._addToZip(path=self._readme_path,              zip_file=population_zip_file, path_in_zip=readme_file)
                    population_zip_file.close()
                    if self._file_names["population"] is not None:
                        os.remove(self._file_names["population"])
                except FileNotFoundError as err:
                    utils.Logger.Log(f"FileNotFoundError Exception: {err}", logging.ERROR)
                    traceback.print_tb(err.__traceback__)
        if self._zip_names['players'] is not None:
            with zipfile.ZipFile(self._zip_names["players"], "w", compression=zipfile.ZIP_DEFLATED) as players_zip_file:
                try:
                    player_file = Path(self._dataset_id) / f"{self._dataset_id}_{self._short_hash}_player-features.{self._extension}"
                    readme_file  = Path(self._dataset_id) / "readme.md"
                    self._addToZip(path=self._file_names["players"], zip_file=players_zip_file, path_in_zip=player_file)
                    self._addToZip(path=self._readme_path,           zip_file=players_zip_file, path_in_zip=readme_file)
                    players_zip_file.close()
                    if self._file_names["players"] is not None:
                        os.remove(self._file_names["players"])
                except FileNotFoundError as err:
                    utils.Logger.Log(f"FileNotFoundError Exception: {err}", logging.ERROR)
                    traceback.print_tb(err.__traceback__)
        if self._zip_names['sessions'] is not None:
            with zipfile.ZipFile(self._zip_names["sessions"], "w", compression=zipfile.ZIP_DEFLATED) as sessions_zip_file:
                try:
                    session_file = Path(self._dataset_id) / f"{self._dataset_id}_{self._short_hash}_session-features.{self._extension}"
                    readme_file  = Path(self._dataset_id) / "readme.md"
                    self._addToZip(path=self._file_names["sessions"], zip_file=sessions_zip_file, path_in_zip=session_file)
                    self._addToZip(path=self._readme_path,            zip_file=sessions_zip_file, path_in_zip=readme_file)
                    sessions_zip_file.close()
                    if self._file_names["sessions"] is not None:
                        os.remove(self._file_names["sessions"])
                except FileNotFoundError as err:
                    utils.Logger.Log(f"FileNotFoundError Exception: {err}", logging.ERROR)
                    traceback.print_tb(err.__traceback__)
        if self._zip_names['events'] is not None:
            with zipfile.ZipFile(self._zip_names["events"], "w", compression=zipfile.ZIP_DEFLATED) as events_zip_file:
                try:
                    events_file = Path(self._dataset_id) / f"{self._dataset_id}_{self._short_hash}_events.{self._extension}"
                    readme_file = Path(self._dataset_id) / "readme.md"
                    self._addToZip(path=self._file_names["events"], zip_file=events_zip_file, path_in_zip=events_file)
                    self._addToZip(path=self._readme_path,          zip_file=events_zip_file, path_in_zip=readme_file)
                    events_zip_file.close()
                    if self._file_names["events"] is not None:
                        os.remove(self._file_names["events"])
                except FileNotFoundError as err:
                    utils.Logger.Log(f"FileNotFoundError Exception: {err}", logging.ERROR)
                    traceback.print_tb(err.__traceback__)

    def _addToZip(self, path, zip_file, path_in_zip) -> None:
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
    def WriteMetadataFile(self, num_sess:int) -> None:
        # First, ensure we have a data directory.
        try:
            self._game_data_dir.mkdir(exist_ok=True, parents=True)
        except Exception as err:
            msg = f"Could not set up folder {self._game_data_dir}. {type(err)} {str(err)}"
            utils.Logger.Log(msg, logging.WARNING)
        else:
            # Second, remove old metas, if they exist.
            start_range = self._date_range['min'].strftime("%Y%m%d") if self._date_range['min'] is not None else "Unknown"
            end_range   = self._date_range['max'].strftime("%Y%m%d") if self._date_range['max'] is not None else "Unknown"
            match_string = f"{self._game_id}_{start_range}_to_{end_range}_\\w*\\.meta"
            old_metas = [f for f in os.listdir(self._game_data_dir) if re.match(match_string, f)]
            for old_meta in old_metas:
                try:
                    utils.Logger.Log(f"Removing old meta file, {old_meta}")
                    os.remove(self._game_data_dir / old_meta)
                except Exception as err:
                    msg = f"Could not remove old meta file {old_meta}. {type(err)} {str(err)}"
                    utils.Logger.Log(msg, logging.WARNING)
            # Third, write the new meta file.
            # calculate the path and name of the metadata file, and open/make it.
            meta_file_path : Path = self._game_data_dir/ f"{self._dataset_id}_{self._short_hash}.meta"
            with open(meta_file_path, "w", encoding="utf-8") as meta_file :
                metadata  = \
                {
                    "game_id"      :self._game_id,
                    "dataset_id"   :self._dataset_id,
                    "ogd_revision" :self._short_hash,
                    "start_date"   :self._date_range['min'].strftime("%m/%d/%Y") if self._date_range['min'] is not None else "Unknown",
                    "end_date"     :self._date_range['max'].strftime("%m/%d/%Y") if self._date_range['max'] is not None else "Unknown",
                    "date_modified":datetime.now().strftime("%m/%d/%Y"),
                    "sessions"     :num_sess,
                    "population_file" :str(self._zip_names['population']) if self._zip_names['population'] else None,
                    "players_file"    :str(self._zip_names['players'])   if self._zip_names['players']   else None,
                    "sessions_file"   :str(self._zip_names['sessions'])   if self._zip_names['sessions']   else None,
                    "events_file"     :str(self._zip_names['events'])     if self._zip_names['events']     else None
                }
                meta_file.write(json.dumps(metadata, indent=4))
                meta_file.close()

    ## Public function to update the list of exported files.
    #  Using the paths of the exported files, and given some other variables for
    #  deriving file metadata, this simply updates the JSON file to the latest
    #  list of files.
    #  @param date_range    The range of dates included in the exported data.
    #  @param num_sess      The number of sessions included in the recent export.
    def UpdateFileExportList(self, num_sess: int) -> None:
        self._backupFileExportList()
        existing_csvs = {}
        try:
            existing_csvs = utils.loadJSONFile(filename="file_list.json", path=self._data_dir)
        except FileNotFoundError as err:
            utils.Logger.Log("file_list.json does not exist.", logging.WARNING)
        except Exception as err:
            msg = f"Could not load file list. {type(err)} {str(err)}"
            utils.Logger.Log(msg, logging.ERROR)
        finally:
            with open(self._data_dir / "file_list.json", "w") as existing_csv_file:
                utils.Logger.Log(f"opened csv file at {existing_csv_file.name}", logging.INFO)
                if not self._game_id in existing_csvs.keys():
                    existing_csvs[self._game_id] = {}
                existing_data = existing_csvs[self._game_id][self._dataset_id] if self._dataset_id in existing_csvs[self._game_id].keys() else None
                population_path = str(self._zip_names["population"]) if self._zip_names["population"] is not None \
                                  else (existing_data["population"] if (existing_data is not None and "population" in existing_data.keys()) else None)
                players_path    = str(self._zip_names["players"]) if self._zip_names["players"] is not None \
                                  else (existing_data["players"] if (existing_data is not None and "players" in existing_data.keys()) else None)
                sessions_path   = str(self._zip_names["sessions"]) if self._zip_names["sessions"] is not None \
                                  else (existing_data["sessions"] if (existing_data is not None and "sessions" in existing_data.keys()) else None)
                events_path     = str(self._zip_names["events"]) if self._zip_names["events"] is not None \
                                  else (existing_data["events"] if (existing_data is not None and "events" in existing_data.keys()) else None)
                existing_csvs[self._game_id][self._dataset_id] = \
                {
                    "ogd_revision" :self._short_hash,
                    "start_date"   :self._date_range['min'].strftime("%m/%d/%Y") if self._date_range['min'] is not None else "Unknown",
                    "end_date"     :self._date_range['max'].strftime("%m/%d/%Y") if self._date_range['max'] is not None else "Unknown",
                    "date_modified":datetime.now().strftime("%m/%d/%Y"),
                    "sessions"     :num_sess,
                    "population_file" :population_path,
                    "players_file"    :players_path,
                    "sessions_file"   :sessions_path,
                    "events_file"     :events_path,
                }
                existing_csv_file.write(json.dumps(existing_csvs, indent=4))

    def _backupFileExportList(self) -> bool:
        try:
            src  : Path = self._data_dir / "file_list.json"
            dest : Path = self._data_dir / "file_list.json.bak"
            if src.exists():
                shutil.copyfile(src=src, dst=dest)
            else:
                utils.Logger.Log(f"Could not back up file_list.json, because it does not exist!", logging.WARN)
        except Exception as err:
            msg = f"{type(err)} {str(err)}"
            utils.Logger.Log(f"Could not back up file_list.json. Got the following error: {msg}", logging.ERROR)
            return False
        else:
            utils.Logger.Log(f"Backed up file_list.json to {dest}", logging.INFO)
            return True
