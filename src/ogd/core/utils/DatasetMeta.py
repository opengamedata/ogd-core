# import standard libraries
import json
import logging
import os
import re
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, IO, List, Optional, Set

# import 3rd-party libraries
from git.repo import Repo
from git.exc import InvalidGitRepositoryError, NoSuchPathError

# import local files
from ogd.core.utils.Logger import Logger
from ogd.core.utils.utils import ExportRow

class DatasetMeta:

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, game_id:str, date_range:Dict[str,Optional[datetime]], dataset_id_default:Optional[str]=None):
        self._game_id    : str = game_id
        self._date_range : Dict[str,Optional[datetime]] = date_range
        self._short_hash : str = DatasetMeta._generateShortHash()
        self._dataset_id : str

        # figure out dataset ID.
        start = self._date_range['min'].strftime("%Y%m%d") if self._date_range['min'] is not None else "UNKNOWN"
        end   = self._date_range['max'].strftime("%Y%m%d") if self._date_range['max'] is not None else "UNKNOWN"
        self._dataset_id = dataset_id_default or f"{self._game_id}_{start}_to_{end}"

    @property
    def GameName(self):
        return self._game_id

    @property
    def DateRange(self) -> Dict[str,Optional[datetime]]:
        return self._date_range

    @property
    def ShortHash(self) -> str:
        return self._short_hash

    @property
    def DatasetID(self) -> str:
        return self._dataset_id

    # *** IMPLEMENT ABSTRACTS ***

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    ## Public function to write out a tiny metadata file for indexing OGD data files.
    def ToFile(self, num_sess:int, path:Path = Path("./"), zip_paths:Dict[str, Optional[Path]] = {}) -> None:
        """Private function to write out a tiny metadata file for indexing OGD data files.
        Using the paths of the exported files, and given some other variables for
        deriving file metadata, this simply outputs a new file_name.meta file.

        :param num_sess: The number of sessions included in the recent export.
        :type num_sess: int
        :param path: The path where the dataset meta file should be written, usually the game's data directory, defaults to Path("./")
        :type path: Path, optional
        """
        # First, ensure we have a data directory.
        try:
            path.mkdir(exist_ok=True, parents=True)
        except Exception as err:
            msg = f"Could not set up folder {path}. {type(err)} {str(err)}"
            Logger.Log(msg, logging.WARNING)
        else:
            # Second, remove old metas, if they exist.
            start_range = self._date_range['min'].strftime("%Y%m%d") if self._date_range['min'] is not None else "Unknown"
            end_range   = self._date_range['max'].strftime("%Y%m%d") if self._date_range['max'] is not None else "Unknown"
            match_string = f"{self._game_id}_{start_range}_to_{end_range}_\\w*\\.meta"
            old_metas = [f for f in os.listdir(path) if re.match(match_string, f)]
            for old_meta in old_metas:
                try:
                    Logger.Log(f"Removing old meta file, {old_meta}")
                    os.remove(path / old_meta)
                except Exception as err:
                    msg = f"Could not remove old meta file {old_meta}. {type(err)} {str(err)}"
                    Logger.Log(msg, logging.WARNING)
            # Third, write the new meta file.
            # calculate the path and name of the metadata file, and open/make it.
            meta_file_path : Path = path / f"{self._dataset_id}_{self._short_hash}.meta"
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
                    "population_file"     : str(zip_paths['population'])           if zip_paths['population']       else None,
                    "population_template" : f'/tree/{self.GameName.lower()}' if zip_paths['population']       else None,
                    "players_file"        : str(zip_paths['players'])              if zip_paths['players']          else None,
                    "players_template"    : f'/tree/{self.GameName.lower()}' if zip_paths['players']          else None,
                    "sessions_file"       : str(zip_paths['sessions'])             if zip_paths['sessions']         else None,
                    "sessions_template"   : f'/tree/{self.GameName.lower()}' if zip_paths['sessions']         else None,
                    "raw_file"            : str(zip_paths['raw_events'])           if zip_paths['raw_events']       else None,
                    "events_template"     : f'/tree/{self.GameName.lower()}' if zip_paths['raw_events']       else None,
                    "events_file"         : str(zip_paths['processed_events'])     if zip_paths['processed_events'] else None,
                    "all_events_template" : f'/tree/{self.GameName.lower()}' if zip_paths['processed_events'] else None
                }
                meta_file.write(json.dumps(metadata, indent=4))
                meta_file.close()

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _generateShortHash() -> str:
        ret_val = "NO_HASH"
        try:
            repo = Repo(search_parent_directories=True)
            if repo.git is not None:
                ret_val = str(repo.git.rev_parse(repo.head.object.hexsha, short=7))
        except InvalidGitRepositoryError as err:
            msg = f"Code is not in a valid Git repository:\n{str(err)}"
            Logger.Log(msg, logging.ERROR)
        except NoSuchPathError as err:
            msg = f"Unable to access proper file paths for Git repository:\n{str(err)}"
            Logger.Log(msg, logging.ERROR)
        finally:
            return ret_val
