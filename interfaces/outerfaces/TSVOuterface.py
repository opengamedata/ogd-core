## import standard libraries
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
from typing import Any, Dict, IO, List, Optional, Set

# import local files
import utils
from interfaces.outerfaces.DataOuterface import DataOuterface
from schemas.ExtractionMode import ExtractionMode
from schemas.ExportMode import ExportMode
from schemas.GameSchema import GameSchema
from schemas.TableSchema import TableSchema
from utils import Logger, ExportRow

class TSVOuterface(DataOuterface):

    # *** BUILT-INS ***

    def __init__(self, game_id:str, export_modes:Set[ExportMode], date_range:Dict[str,Optional[datetime]], data_dir:str, extension:str="tsv", dataset_id:Optional[str]=None):
        super().__init__(game_id=game_id, config={})
        self._file_paths   : Dict[str,Optional[Path]] = {"population":None, "players":None, "sessions":None, "events":None}
        self._zip_names    : Dict[str,Optional[Path]] = {"population":None, "players":None, "sessions":None, "events":None}
        self._files        : Dict[str,Optional[IO]]   = {"population":None, "players":None, "sessions":None, "events":None}
        self._data_dir     : Path = Path("./" + data_dir)
        self._game_data_dir: Path = self._data_dir / self._game_id
        self._readme_path  : Path = self._game_data_dir/ "readme.md"
        self._extension    : str  = extension
        self._date_range   : Dict[str,Optional[datetime]] = date_range
        self._dataset_id   : str  = ""
        self._short_hash   : str  = ""
        self._sess_count   : int  = 0
        # figure out dataset ID.
        start = self._date_range['min'].strftime("%Y%m%d") if self._date_range['min'] is not None else "UNKNOWN"
        end   = self._date_range['max'].strftime("%Y%m%d") if self._date_range['max'] is not None else "UNKNOWN"
        self._dataset_id = dataset_id or f"{self._game_id}_{start}_to_{end}"
        # get hash
        try:
            repo = git.Repo(search_parent_directories=True)
            if repo.git is not None:
                self._short_hash = str(repo.git.rev_parse(repo.head.object.hexsha, short=7))
        except InvalidGitRepositoryError as err:
            msg = f"Code is not in a valid Git repository:\n{str(err)}"
            Logger.Log(msg, logging.ERROR)
        except NoSuchPathError as err:
            msg = f"Unable to access proper file paths for Git repository:\n{str(err)}"
            Logger.Log(msg, logging.ERROR)
        # then set up our paths, and ensure each exists.
        base_file_name    : str  = f"{self._dataset_id}_{self._short_hash}"
        # finally, generate file names.
        if ExportMode.EVENTS in export_modes:
            self._file_paths['events']     = self._game_data_dir / f"{base_file_name}_events.{self._extension}"
            self._zip_names['events']      = self._game_data_dir / f"{base_file_name}_events.zip"
        if ExportMode.SESSION in export_modes:
            self._file_paths['sessions']   = self._game_data_dir / f"{base_file_name}_session-features.{self._extension}"
            self._zip_names['sessions']    = self._game_data_dir / f"{base_file_name}_session-features.zip"
        if ExportMode.PLAYER in export_modes:
            self._file_paths['players']   = self._game_data_dir / f"{base_file_name}_player-features.{self._extension}"
            self._zip_names['players']    = self._game_data_dir / f"{base_file_name}_player-features.zip"
        if ExportMode.POPULATION in export_modes:
            self._file_paths['population'] = self._game_data_dir / f"{base_file_name}_population-features.{self._extension}"
            self._zip_names['population']  = self._game_data_dir / f"{base_file_name}_population-features.zip"
        self.Open()

    def __del__(self):
        self.Close()

    # *** IMPLEMENT ABSTRACTS ***

    def _open(self) -> bool:
        self._game_data_dir.mkdir(exist_ok=True, parents=True)
        self._files['events']     = open(self._file_paths['events'],   "w+", encoding="utf-8") if (self._file_paths['events'] is not None) else None
        self._files['sessions']   = open(self._file_paths['sessions'], "w+", encoding="utf-8") if (self._file_paths['sessions'] is not None) else None
        self._files['players']    = open(self._file_paths['players'],  "w+", encoding="utf-8") if (self._file_paths['players'] is not None) else None
        self._files['population'] = open(self._file_paths['population'], "w+", encoding="utf-8") if (self._file_paths['population'] is not None) else None
        return True

    def _close(self) -> bool:
        Logger.Log(f"Closing TSV outerface...")
        try:
            # before we zip stuff up, let's check if the readme is in place:
            readme = open(self._readme_path, mode='r')
        except FileNotFoundError:
            # if not in place, generate the readme
            Logger.Log(f"Missing readme for {self._game_id}, generating new readme...", logging.WARNING, depth=1)
            readme_path = Path("./data") / self._game_id
            game_schema  : GameSchema  = GameSchema(schema_name=self._game_id, schema_path=Path(f"./games/{self._game_id}"))
            table_schema = TableSchema.FromID(game_id=self._game_id)
            TSVOuterface.GenerateReadme(game_schema=game_schema, table_schema=table_schema, path=readme_path)
        else:
            # otherwise, readme is there, so just close it and move on.
            readme.close()
        finally:
            self._closeFiles()
            self._zipFiles()
            self._writeMetadataFile(num_sess=self._sess_count)
            self._updateFileExportList(num_sess=self._sess_count)
            return True

    def _destination(self, mode:ExportMode) -> str:
        ret_val = ""
        if mode == ExportMode.EVENTS:
            ret_val = str(self._file_paths['events'])
        elif mode == ExportMode.SESSION:
            ret_val = str(self._file_paths['sessions'])
        elif mode == ExportMode.PLAYER:
            ret_val = str(self._file_paths['players'])
        elif mode == ExportMode.POPULATION:
            ret_val = str(self._file_paths['population'])
        return ret_val

    def _writeEventsHeader(self, header:List[str]) -> None:
        cols = TSVOuterface._cleanSpecialChars(vals=header)
        cols_line = "\t".join(cols) + "\n"
        if self._files['events'] is not None:
            self._files['events'].writelines(cols_line)
        else:
            Logger.Log("No events file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write("".join(cols_line))

    def _writeSessionHeader(self, header:List[str]) -> None:
        cols = TSVOuterface._cleanSpecialChars(vals=header)
        cols_line = "\t".join(cols) + "\n"
        if self._files['sessions'] is not None:
            self._files['sessions'].writelines(cols_line)
        else:
            Logger.Log("No session file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write("".join(cols_line))

    def _writePlayerHeader(self, header:List[str]) -> None:
        cols = TSVOuterface._cleanSpecialChars(vals=header)
        cols_line = "\t".join(cols) + "\n"
        if self._files['players'] is not None:
            self._files['players'].writelines(cols_line)
        else:
            Logger.Log("No player file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write("".join(cols_line))

    def _writePopulationHeader(self, header:List[str]) -> None:
        cols = TSVOuterface._cleanSpecialChars(vals=header)
        cols_line = "\t".join(cols) + "\n"
        if self._files['population'] is not None:
            self._files['population'].writelines(cols_line)
        else:
            Logger.Log("No population file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write("".join(cols_line))

    def _writeEventLines(self, events:List[ExportRow]) -> None:
        event_strs = [TSVOuterface._cleanSpecialChars(vals=[str(item) for item in event]) for event in events]
        event_lines = ["\t".join(event) + "\n" for event in event_strs]
        if self._files['events'] is not None:
            self._files['events'].writelines(event_lines)
        else:
            Logger.Log("No events file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write("".join(event_lines))

    def _writeSessionLines(self, sessions:List[ExportRow]) -> None:
        self._sess_count += len(sessions)
        _session_feats = [TSVOuterface._cleanSpecialChars(vals=sess) for sess in sessions]
        _session_lines = ["\t".join(sess) + "\n" for sess in _session_feats]
        if self._files['sessions'] is not None:
            self._files['sessions'].writelines(_session_lines)
        else:
            Logger.Log("No session file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write("".join(_session_lines))

    def _writePlayerLines(self, players:List[ExportRow]) -> None:
        _player_feats = [TSVOuterface._cleanSpecialChars(vals=play) for play in players]
        _player_lines = ["\t".join(play) + "\n" for play in _player_feats]
        if self._files['players'] is not None:
            self._files['players'].writelines(_player_lines)
        else:
            Logger.Log("No player file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write("".join(_player_lines))

    def _writePopulationLines(self, populations:List[ExportRow]) -> None:
        _pop_feats = [TSVOuterface._cleanSpecialChars(vals=pop) for pop in populations]
        _pop_lines = ["\t".join(pop) + "\n" for pop in _pop_feats]
        if self._files['population'] is not None:
            self._files['population'].writelines(_pop_lines)
        else:
            Logger.Log("No population file available, writing to standard output instead.", logging.WARN)
            sys.stdout.write("".join(_pop_lines))

    # *** PUBLIC STATICS ***

    @staticmethod
    def GenerateReadme(game_schema:GameSchema, table_schema:TableSchema, path:Path = Path("./")):
        try:
            os.makedirs(name=path, exist_ok=True)
            with open(path / "readme.md", "w") as readme:
                # 1. Open files with game-specific readme data, and global db changelog.
                game_schema_dir = Path(f"./games/{game_schema.GameName}/schemas")
                try:
                    with open(game_schema_dir / f"{game_schema.GameName}_readme_src.md", "r") as readme_src:
                        readme.write(readme_src.read())
                except FileNotFoundError as err:
                    readme.write("No game readme prepared")
                    Logger.Log(f"Could not find {game_schema.GameName}_readme_src", logging.WARNING)
                finally:
                    readme.write("\n\n")
                # 2. Use schema to write feature & column descriptions to the readme.
                meta = TSVOuterface.GenCSVMetadata(game_schema=game_schema, table_schema=table_schema)
                readme.write(meta)
                # 3. Append any important data from the data changelog.
                changelog_dir = Path(f"./schemas/")
                try:
                    with open(changelog_dir / "database_changelog_src.md", "r") as changelog_src:
                        readme.write(changelog_src.read())
                except FileNotFoundError as err:
                    readme.write("No changelog prepared")
                    Logger.Log(f"Could not find changelog_src", logging.WARNING)
        except FileNotFoundError as err:
            Logger.Log(f"Could not open readme.md for writing.", logging.ERROR)
            traceback.print_tb(err.__traceback__)
        else:
            Logger.Log(f"Wrote readme file to {path}/readme.md", logging.INFO)

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
        f"{table_schema.AsMarkdown}",
        "",
        f"{game_schema.AsMarkdown}",
        ""])
        return template_str

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _cleanSpecialChars(vals:List[Any], tab_width:int=3) -> List[str]:
        # check all return values for strings, and ensure no newlines or tabs get through, as they could throw off our outputs.
        for i in range(len(vals)):
            vals[i] = str(vals[i]).replace('\n', ' ').replace('\t', ' '*tab_width)
        return vals

    @staticmethod
    def _addToZip(path, zip_file, path_in_zip) -> None:
        try:
            zip_file.write(path, path_in_zip)
        except FileNotFoundError as err:
            Logger.Log(str(err), logging.ERROR)
            traceback.print_tb(err.__traceback__)

    # *** PRIVATE METHODS ***

    def _closeFiles(self) -> None:
        if self._files['events'] is not None:
            self._files['events'].close()
        if self._files['sessions'] is not None:
            self._files['sessions'].close()
        if self._files['players'] is not None:
            self._files['players'].close()
        if self._files['population'] is not None:
            self._files['population'].close()

    def _zipFiles(self) -> None:
        existing_datasets = {}
        try:
            file_directory = utils.loadJSONFile(filename="file_list.json", path=self._data_dir)
            existing_datasets = file_directory.get(self._game_id, {})
        except FileNotFoundError as err:
            Logger.Log("file_list.json does not exist.", logging.WARNING)
        except json.decoder.JSONDecodeError as err:
            Logger.Log(f"file_list.json has invalid format: {str(err)}.", logging.WARNING)
        # if we have already done this dataset before, rename old zip files
        # (of course, first check if we ever exported this game before).
        existing_meta = existing_datasets.get(self._dataset_id, None)
        if existing_meta is not None:
            _existing_events_file  = existing_meta.get('events_file', None)
            _existing_sess_file    = existing_meta.get('sessions_file', None)
            _existing_players_file = existing_meta.get('players_file', None)
            _existing_pop_file     = existing_meta.get('population_file', None)
            try:
                if _existing_events_file is not None and self._zip_names['events'] is not None:
                    Logger.Log(f"Renaming {str(_existing_events_file)} -> {self._zip_names['events']}", logging.DEBUG)
                    os.rename(_existing_events_file, str(self._zip_names['events']))
                if _existing_sess_file is not None and self._zip_names['sessions'] is not None:
                    Logger.Log(f"Renaming {str(_existing_sess_file)} -> {self._zip_names['sessions']}", logging.DEBUG)
                    os.rename(_existing_sess_file, str(self._zip_names['sessions']))
                if _existing_players_file is not None and self._zip_names['players'] is not None:
                    Logger.Log(f"Renaming {str(_existing_players_file)} -> {self._zip_names['players']}", logging.DEBUG)
                    os.rename(_existing_players_file, str(self._zip_names['players']))
                if _existing_pop_file is not None and self._zip_names['population'] is not None:
                    Logger.Log(f"Renaming {str(_existing_pop_file)} -> {self._zip_names['population']}", logging.DEBUG)
                    os.rename(_existing_pop_file, str(self._zip_names['population']))
            except Exception as err:
                msg = f"Error while setting up zip files! {type(err)} : {err}"
                Logger.Log(msg, logging.ERROR)
                traceback.print_tb(err.__traceback__)
        # for each file, try to save out the csv/tsv to a file - if it's one that should be exported, that is.
        if self._zip_names['population'] is not None:
            with zipfile.ZipFile(self._zip_names["population"], "w", compression=zipfile.ZIP_DEFLATED) as population_zip_file:
                try:
                    population_file = Path(self._dataset_id) / f"{self._dataset_id}_{self._short_hash}_population-features.{self._extension}"
                    readme_file  = Path(self._dataset_id) / "readme.md"
                    TSVOuterface._addToZip(path=self._file_paths["population"], zip_file=population_zip_file, path_in_zip=population_file)
                    TSVOuterface._addToZip(path=self._readme_path,              zip_file=population_zip_file, path_in_zip=readme_file)
                    population_zip_file.close()
                    if self._file_paths["population"] is not None:
                        os.remove(self._file_paths["population"])
                except FileNotFoundError as err:
                    Logger.Log(f"FileNotFoundError Exception: {err}", logging.ERROR)
                    traceback.print_tb(err.__traceback__)
        if self._zip_names['players'] is not None:
            with zipfile.ZipFile(self._zip_names["players"], "w", compression=zipfile.ZIP_DEFLATED) as players_zip_file:
                try:
                    player_file = Path(self._dataset_id) / f"{self._dataset_id}_{self._short_hash}_player-features.{self._extension}"
                    readme_file  = Path(self._dataset_id) / "readme.md"
                    TSVOuterface._addToZip(path=self._file_paths["players"], zip_file=players_zip_file, path_in_zip=player_file)
                    TSVOuterface._addToZip(path=self._readme_path,           zip_file=players_zip_file, path_in_zip=readme_file)
                    players_zip_file.close()
                    if self._file_paths["players"] is not None:
                        os.remove(self._file_paths["players"])
                except FileNotFoundError as err:
                    Logger.Log(f"FileNotFoundError Exception: {err}", logging.ERROR)
                    traceback.print_tb(err.__traceback__)
        if self._zip_names['sessions'] is not None:
            with zipfile.ZipFile(self._zip_names["sessions"], "w", compression=zipfile.ZIP_DEFLATED) as sessions_zip_file:
                try:
                    session_file = Path(self._dataset_id) / f"{self._dataset_id}_{self._short_hash}_session-features.{self._extension}"
                    readme_file  = Path(self._dataset_id) / "readme.md"
                    TSVOuterface._addToZip(path=self._file_paths["sessions"], zip_file=sessions_zip_file, path_in_zip=session_file)
                    TSVOuterface._addToZip(path=self._readme_path,            zip_file=sessions_zip_file, path_in_zip=readme_file)
                    sessions_zip_file.close()
                    if self._file_paths["sessions"] is not None:
                        os.remove(self._file_paths["sessions"])
                except FileNotFoundError as err:
                    Logger.Log(f"FileNotFoundError Exception: {err}", logging.ERROR)
                    traceback.print_tb(err.__traceback__)
        if self._zip_names['events'] is not None:
            with zipfile.ZipFile(self._zip_names["events"], "w", compression=zipfile.ZIP_DEFLATED) as events_zip_file:
                try:
                    events_file = Path(self._dataset_id) / f"{self._dataset_id}_{self._short_hash}_events.{self._extension}"
                    readme_file = Path(self._dataset_id) / "readme.md"
                    TSVOuterface._addToZip(path=self._file_paths["events"], zip_file=events_zip_file, path_in_zip=events_file)
                    TSVOuterface._addToZip(path=self._readme_path,          zip_file=events_zip_file, path_in_zip=readme_file)
                    events_zip_file.close()
                    if self._file_paths["events"] is not None:
                        os.remove(self._file_paths["events"])
                except FileNotFoundError as err:
                    Logger.Log(f"FileNotFoundError Exception: {err}", logging.ERROR)
                    traceback.print_tb(err.__traceback__)

    ## Public function to write out a tiny metadata file for indexing OGD data files.
    #  Using the paths of the exported files, and given some other variables for
    #  deriving file metadata, this simply outputs a new file_name.meta file.
    #  @param date_range    The range of dates included in the exported data.
    #  @param num_sess      The number of sessions included in the recent export.
    def _writeMetadataFile(self, num_sess:int) -> None:
        # First, ensure we have a data directory.
        try:
            self._game_data_dir.mkdir(exist_ok=True, parents=True)
        except Exception as err:
            msg = f"Could not set up folder {self._game_data_dir}. {type(err)} {str(err)}"
            Logger.Log(msg, logging.WARNING)
        else:
            # Second, remove old metas, if they exist.
            start_range = self._date_range['min'].strftime("%Y%m%d") if self._date_range['min'] is not None else "Unknown"
            end_range   = self._date_range['max'].strftime("%Y%m%d") if self._date_range['max'] is not None else "Unknown"
            match_string = f"{self._game_id}_{start_range}_to_{end_range}_\\w*\\.meta"
            old_metas = [f for f in os.listdir(self._game_data_dir) if re.match(match_string, f)]
            for old_meta in old_metas:
                try:
                    Logger.Log(f"Removing old meta file, {old_meta}")
                    os.remove(self._game_data_dir / old_meta)
                except Exception as err:
                    msg = f"Could not remove old meta file {old_meta}. {type(err)} {str(err)}"
                    Logger.Log(msg, logging.WARNING)
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
    def _updateFileExportList(self, num_sess: int) -> None:
        self._backupFileExportList()
        file_directory = {}
        existing_datasets = {}
        try:
            file_directory = utils.loadJSONFile(filename="file_list.json", path=self._data_dir)
        except FileNotFoundError as err:
            Logger.Log("file_list.json does not exist.", logging.WARNING)
        except json.decoder.JSONDecodeError as err:
            Logger.Log(f"file_list.json has invalid format: {str(err)}.", logging.WARNING)
        finally:
            if not self._game_id in file_directory.keys():
                file_directory[self._game_id] = {}
            existing_datasets  = file_directory[self._game_id]
            with open(self._data_dir / "file_list.json", "w") as existing_csv_file:
                Logger.Log(f"Opened file list for writing at {existing_csv_file.name}", logging.INFO)
                existing_metadata = existing_datasets.get(self._dataset_id, {})
                population_path = self._zip_names.get("population") or existing_metadata.get("population")
                players_path    = self._zip_names.get("players")    or existing_metadata.get("players")
                sessions_path   = self._zip_names.get("sessions")   or existing_metadata.get("sessions")
                events_path     = self._zip_names.get("events")     or existing_metadata.get("events")
                file_directory[self._game_id][self._dataset_id] = \
                {
                    "ogd_revision" :self._short_hash,
                    "start_date"   :self._date_range['min'].strftime("%m/%d/%Y") if self._date_range['min'] is not None else "Unknown",
                    "end_date"     :self._date_range['max'].strftime("%m/%d/%Y") if self._date_range['max'] is not None else "Unknown",
                    "date_modified":datetime.now().strftime("%m/%d/%Y"),
                    "sessions"     :num_sess,
                    "population_file" :str(population_path) if population_path is not None else None,
                    "players_file"    :str(players_path)    if players_path    is not None else None,
                    "sessions_file"   :str(sessions_path)   if sessions_path   is not None else None,
                    "events_file"     :str(events_path)     if events_path     is not None else None,
                }
                existing_csv_file.write(json.dumps(existing_datasets, indent=4))

    def _backupFileExportList(self) -> bool:
        try:
            src  : Path = self._data_dir / "file_list.json"
            dest : Path = self._data_dir / "file_list.json.bak"
            if src.exists():
                shutil.copyfile(src=src, dst=dest)
            else:
                Logger.Log(f"Could not back up file_list.json, because it does not exist!", logging.WARN)
        except Exception as err:
            msg = f"{type(err)} {str(err)}"
            Logger.Log(f"Could not back up file_list.json. Got the following error: {msg}", logging.ERROR)
            return False
        else:
            Logger.Log(f"Backed up file_list.json to {dest}", logging.INFO)
            return True