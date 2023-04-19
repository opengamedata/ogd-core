# import standard libraries
import logging
from pathlib import Path
from typing import Any, Dict, Optional
# import local files
from schemas.config_schemas.IndexingSchema import FileIndexingSchema
from schemas.config_schemas.SSHSchema import SSHSchema
from schemas.config_schemas.GameSourceSchema import GameSourceSchema
from schemas.config_schemas.DataSourceSchema import DataSourceSchema
from schemas.Schema import Schema
from utils import Logger

class ConfigSchema(Schema):
    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._data_dir   : Path
        self._log_file   : bool
        self._batch_size : int
        self._dbg_level  : int
        self._fail_fast  : bool
        self._file_idx   : FileIndexingSchema
        self._ssh_config : SSHSchema
        self._data_src   : Dict[str, DataSourceSchema]
        self._game_src_map : Dict[str, GameSourceSchema]

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} base config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        if "DATA_DIR" in all_elements.keys():
            self._data_dir = ConfigSchema._parseDataDir(all_elements["DATA_DIR"])
        else:
            self._data_dir = Path("./data/")
            # No need to warn if outdated DATA_DIR does not exist.
            # Logger.Log(f"{name} config does not have a 'DATA_DIR' element; defaulting to data_dir={self._data_dir}", logging.WARN)
        if "LOG_FILE" in all_elements.keys():
            self._log_file = ConfigSchema._parseLogFile(all_elements["log_file"])
        else:
            self._log_file = False
            Logger.Log(f"{name} config does not have a 'LOG_FILE' element; defaulting to log_file={self._log_file}", logging.WARN)
        if "BATCH_SIZE" in all_elements.keys():
            self._batch_size_name = ConfigSchema._parseBatchSize(all_elements["BATCH_SIZE"])
        else:
            self._batch_size_name = 500
            Logger.Log(f"{name} config does not have a 'BATCH_SIZE' element; defaulting to batch_size={self._batch_size_name}", logging.WARN)
        if "DEBUG_LEVEL" in all_elements.keys():
            self._dbg_level = ConfigSchema._parseDebugLevel(all_elements["DEBUG_LEVEL"])
        else:
            self._dbg_level = logging.INFO
            Logger.Log(f"{name} config does not have a 'DEBUG_LEVEL' element; defaulting to dbg_level={self._dbg_level}", logging.WARN)
        if "FAIL_FAST" in all_elements.keys():
            self._fail_fast = ConfigSchema._parseFailFast(all_elements["FAIL_FAST"])
        else:
            self._fail_fast = False
            Logger.Log(f"{name} config does not have a 'FAIL_FAST' element; defaulting to fail_fast={self._fail_fast}", logging.WARN)
        if "FILE_INDEXING" in all_elements.keys():
            self._file_indexing = ConfigSchema._parseFileIndexing(all_elements["FILE_INDEXING"])
        else:
            self._file_indexing = FileIndexingSchema(name="FILE_INDEXING", all_elements={})
            Logger.Log(f"{name} config does not have a 'FILE_INDEXING' element; defaulting to file_indexing={self._file_indexing}", logging.WARN)
        if "SSH_CONFIG" in all_elements.keys():
            self._ssh_config = ConfigSchema._parseSSHConfig(all_elements["SSH_CONFIG"])
        else:
            self._ssh_config = SSHSchema(name="SSH_CONFIG", all_elements={})
            Logger.Log(f"{name} config does not have a 'SSH_CONFIG' element; defaulting to ssh_config={self._ssh_config}", logging.WARN)
        if "GAME_SOURCES" in all_elements.keys():
            self._game_sources = ConfigSchema._parseDataSources(all_elements["GAME_SOURCES"])
        else:
            self._game_sources = {}
            Logger.Log(f"{name} config does not have a 'GAME_SOURCES' element; defaulting to game_sources={self._game_sources}", logging.WARN)
        if "GAME_SOURCE_MAP" in all_elements.keys():
            self._game_source_map = ConfigSchema._parseGameSourceMap(all_elements["GAME_SOURCE_MAP"])
        else:
            self._game_source_map = {}
            Logger.Log(f"{name} config does not have a 'GAME_SOURCE_MAP' element; defaulting to game_source_map={self._game_source_map}", logging.WARN)

        _leftovers = { key : val for key,val in all_elements.items() if key not in {"schema", "source", "table", "credential"} }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def DataDirectory(self) -> Path:
        if self.FileIndexConfig.LocalDirectory is not None:
            return self.FileIndexConfig.LocalDirectory
        else:
            Logger.Log(f"Did not have a local directory in FILE_INDEXING config item, falling back on DATA_DIR config item.")
            return self._data_dir

    @property
    def UseLogFile(self) -> bool:
        return self._log_file

    @property
    def BatchSize(self) -> int:
        return self._batch_size

    @property
    def DebugLevel(self) -> int:
        return self._dbg_level

    @property
    def FailFast(self) -> bool:
        return self._fail_fast

    @property
    def FileIndexConfig(self) -> FileIndexingSchema:
        return self._file_idx

    @property
    def SSHConfig(self) -> SSHSchema:
        return self._ssh_config

    @property
    def DataSources(self) -> Dict[str, DataSourceSchema]:
        return self._data_src

    @property
    def GameSourceMap(self) -> Dict[str, GameSourceSchema]:
        return self._game_source_map

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}"
        return ret_val

    @staticmethod
    def _parseDataDir(dir) -> Path:
        ret_val : Path
        if isinstance(dir, Path):
            ret_val = dir
        elif isinstance(dir, str):
            ret_val = Path(dir)
        else:
            ret_val = Path(str(dir))
            Logger.Log(f"Config data dir was unexpected type {type(dir)}, defaulting to Path(str(dir))={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseLogFile(use_log) -> bool:
        ret_val : bool
        if isinstance(use_log, bool):
            ret_val = use_log
        else:
            ret_val = False
            Logger.Log(f"Config to use log file was unexpected type {type(use_log)}, defaulting to False.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseBatchSize(batch_size) -> int:
        ret_val : int
        if isinstance(batch_size, int):
            ret_val = batch_size
        elif isinstance(batch_size, str):
            ret_val = int(batch_size)
        else:
            ret_val = int(str(batch_size))
            Logger.Log(f"Config batch size was unexpected type {type(batch_size)}, defaulting to int(str(batch_size))={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDebugLevel(level) -> int:
        ret_val : int
        if isinstance(level, str):
            match level.upper():
                case "ERROR":
                    ret_val = logging.ERROR
                case "WARNING" | "WARN":
                    ret_val = logging.WARN
                case "INFO":
                    ret_val = logging.INFO
                case "DEBUG":
                    ret_val = logging.DEBUG
                case _:
                    ret_val = logging.INFO
                    Logger.Log(f"Config debug level had unexpected value {level}, defaulting to logging.INFO.", logging.WARN)
        else:
            ret_val = logging.INFO
            Logger.Log(f"Config debug level was unexpected type {type(level)}, defaulting to logging.INFO.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseFailFast(fail_fast) -> bool:
        ret_val : bool
        if isinstance(fail_fast, bool):
            ret_val = fail_fast
        elif isinstance(fail_fast, str):
            match fail_fast.upper():
                case "TRUE":
                    ret_val = True
                case "FALSE":
                    ret_val = False
                case _:
                    ret_val = False
                    Logger.Log(f"Config fail fast had unexpected value {fail_fast}, defaulting to False.", logging.WARN)
        else:
            ret_val = False
            Logger.Log(f"Config fail fast was unexpected type {type(fail_fast)}, defaulting to False.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseFileIndexing(indexing) -> FileIndexingSchema:
        ret_val : FileIndexingSchema
        if isinstance(indexing, dict):
            ret_val = FileIndexingSchema(name="FILE_INDEXING", all_elements=indexing)
        else:
            ret_val = FileIndexingSchema(name="FILE_INDEXING", all_elements={})
            Logger.Log(f"Config file indexing was unexpected type {type(indexing)}, defaulting to default indexing config: {ret_val.AsMarkdown}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseSSHConfig(ssh) -> SSHSchema:
        ret_val : SSHSchema
        if isinstance(ssh, dict):
            ret_val = SSHSchema(name="SSH_CONFIG", all_elements=ssh)
        else:
            ret_val = SSHSchema(name="SSH_CONFIG", all_elements={})
            Logger.Log(f"Config ssh config was unexpected type {type(ssh)}, defaulting to default ssh config: {ret_val.AsMarkdown}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDataSources(sources) -> Dict[str, DataSourceSchema]:
        ret_val : Dict[str, DataSourceSchema]
        if isinstance(sources, dict):
            ret_val = { key : DataSourceSchema(name=val, all_elements=val) for key, val in sources.items() }
        else:
            ret_val = {}
            Logger.Log(f"Config data sources was unexpected type {type(sources)}, defaulting to empty dict: {ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseGameSourceMap(sources) -> Dict[str, GameSourceSchema]:
        ret_val : Dict[str, GameSourceSchema]
        if isinstance(sources, dict):
            ret_val = { key : GameSourceSchema(name=val, all_elements=val) for key, val in sources.items() }
        else:
            ret_val = {}
            Logger.Log(f"Config game source map was unexpected type {type(sources)}, defaulting to empty dict: {ret_val}.", logging.WARN)
        return ret_val