# import standard libraries
import logging
from pathlib import Path
from typing import Any, Dict
# import local files
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
        self._file_idx   : Dict[str, Path | str]
        self._ssh_config : Dict[str, str | int]
        self._data_src   : Dict[str, DataSourceSchema]
        self._game_src_map : Dict[str, GameSourceSchema]

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} base config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        if "DATA_DIR" in all_elements.keys():
            self._data_dir = ConfigSchema._parseDataDir(all_elements["DATA_DIR"])
        else:
            self._data_dir = Path("./data/")
            Logger.Log(f"{name} config does not have a 'DATA_DIR' element; defaulting to data_dir={self._data_dir}", logging.WARN)
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
            self._file_indexing = {}
            Logger.Log(f"{name} config does not have a 'FILE_INDEXING' element; defaulting to file_indexing={self._file_indexing}", logging.WARN)
        if "SSH_CONFIG" in all_elements.keys():
            self._ssh_config = ConfigSchema._parseSSHConfig(all_elements["SSH_CONFIG"])
        else:
            self._ssh_config = {}
            Logger.Log(f"{name} config does not have a 'SSH_CONFIG' element; defaulting to ssh_config={self._ssh_config}", logging.WARN)
        if "GAME_SOURCES" in all_elements.keys():
            self._game_sources = ConfigSchema._parseGameSources(all_elements["GAME_SOURCES"])
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
    def FileIndexConfig(self) -> Dict[str, Path | str]:
        return self._file_idx

    @property
    def SSHConfig(self) -> Dict[str, str | int]:
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
    def _parseSchema(schema) -> str:
        ret_val : str
        if isinstance(schema, str):
            ret_val = schema
        else:
            ret_val = str(schema)
            Logger.Log(f"Game Source schema type was unexpected type {type(schema)}, defaulting to str(schema)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseSource(source) -> str:
        ret_val : str
        if isinstance(source, str):
            ret_val = source
        else:
            ret_val = str(source)
            Logger.Log(f"Game Source source name was unexpected type {type(source)}, defaulting to str(source)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseTableName(table) -> str:
        ret_val : str
        if isinstance(table, str):
            ret_val = table
        else:
            ret_val = str(table)
            Logger.Log(f"Game Source table name was unexpected type {type(table)}, defaulting to str(table)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseCredential(credential) -> str:
        ret_val : str
        if isinstance(credential, str):
            ret_val = credential
        else:
            ret_val = str(credential)
            Logger.Log(f"Game Source credential type was unexpected type {type(credential)}, defaulting to str(credential)={ret_val}.", logging.WARN)
        return ret_val