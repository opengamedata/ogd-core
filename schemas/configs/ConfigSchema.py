# import standard libraries
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Type
# import local files
from schemas.configs.IndexingSchema import FileIndexingSchema
from schemas.data_sources.GameSourceSchema import GameSourceSchema
from schemas.data_sources.DataHostConfig import DataHostConfig
from schemas.data_sources.BigQueryHostConfig import BigQuerySchema
from schemas.data_sources.FileHostConfig import FileHostConfig
from schemas.data_sources.MySQLHostConfig import MySQLSchema
from schemas.configs.LegacyConfigSchema import LegacyConfigSchema
from schemas.Schema import Schema
from utils.Logger import Logger

class ConfigSchema(Schema):
    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._log_file   : bool
        self._batch_size : int
        self._dbg_level  : int
        self._fail_fast  : bool
        self._file_idx   : FileIndexingSchema
        self._data_src   : Dict[str, DataHostConfig]
        self._game_src_map : Dict[str, GameSourceSchema]

        _used = set()
        self._legacy_elems : LegacyConfigSchema = LegacyConfigSchema(name=f"{name} Legacy", all_elements=all_elements)
        if "LOG_FILE" in all_elements.keys():
            _used.add("LOG_FILE")
            self._log_file = ConfigSchema._parseLogFile(all_elements["LOG_FILE"])
        else:
            self._log_file = False
            Logger.Log(f"{name} config does not have a 'LOG_FILE' element; defaulting to log_file={self._log_file}", logging.WARN)
        if "BATCH_SIZE" in all_elements.keys():
            _used.add("BATCH_SIZE")
            self._batch_size = ConfigSchema._parseBatchSize(all_elements["BATCH_SIZE"])
        else:
            self._batch_size = 500
            Logger.Log(f"{name} config does not have a 'BATCH_SIZE' element; defaulting to batch_size={self._batch_size}", logging.WARN)
        if "DEBUG_LEVEL" in all_elements.keys():
            _used.add("DEBUG_LEVEL")
            self._dbg_level = ConfigSchema._parseDebugLevel(all_elements["DEBUG_LEVEL"])
        else:
            self._dbg_level = logging.INFO
            Logger.Log(f"{name} config does not have a 'DEBUG_LEVEL' element; defaulting to dbg_level={self._dbg_level}", logging.WARN)
        if "FAIL_FAST" in all_elements.keys():
            _used.add("FAIL_FAST")
            self._fail_fast = ConfigSchema._parseFailFast(all_elements["FAIL_FAST"])
        else:
            self._fail_fast = False
            Logger.Log(f"{name} config does not have a 'FAIL_FAST' element; defaulting to fail_fast={self._fail_fast}", logging.WARN)
        if "FILE_INDEXING" in all_elements.keys():
            _used.add("FILE_INDEXING")
            self._file_idx = ConfigSchema._parseFileIndexing(all_elements["FILE_INDEXING"])
        else:
            _fallback_elems = { "LOCAL_DIR" : self._legacy_elems.DataDirectory }
            self._file_idx = FileIndexingSchema(name="FILE_INDEXING", all_elements=_fallback_elems)
            Logger.Log(f"{name} config does not have a 'FILE_INDEXING' element; defaulting to file_indexing={self._file_idx}", logging.WARN)
        if "DATA_HOSTS" in all_elements.keys():
            _used.add("DATA_HOSTS")
            self._data_src = ConfigSchema._parseDataSources(all_elements["DATA_HOSTS"])
        else:
            self._data_src = {}
            Logger.Log(f"{name} config does not have a 'DATA_HOSTS' element; defaulting to game_sources={self._data_src}", logging.WARN)
        if "GAME_SOURCE_MAP" in all_elements.keys():
            _used.add("GAME_SOURCE_MAP")
            self._game_src_map = ConfigSchema._parseGameSourceMap(map=all_elements["GAME_SOURCE_MAP"], sources=self._data_src)
        else:
            self._game_src_map = {}
            Logger.Log(f"{name} config does not have a 'GAME_SOURCE_MAP' element; defaulting to game_source_map={self._game_src_map}", logging.WARN)
        if "GAME_DESTINATION_MAP" in all_elements.keys():
            _used.add("GAME_DESTINATION_MAP")
            self._game_dest_map = ConfigSchema._parseGameDestMap(map=all_elements["GAME_DESTINATION_MAP"], sources=self._data_src)
        else:
            self._game_dest_map = {}
            Logger.Log(f"{name} config does not have a 'GAME_DESTINATION_MAP' element; defaulting to game_dest_map={self._game_dest_map}", logging.WARN)

        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def DataDirectory(self) -> Path:
        return self.FileIndexConfig.LocalDirectory

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
    def DataSources(self) -> Dict[str, DataHostConfig]:
        return self._data_src

    @property
    def GameSourceMap(self) -> Dict[str, GameSourceSchema]:
        return self._game_src_map

    @property
    def GameDestinationMap(self) -> Dict[str, GameSourceSchema]:
        return self._game_dest_map

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}"
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
    def _parseDataSources(sources) -> Dict[str, DataHostConfig]:
        ret_val : Dict[str, DataHostConfig]
        if isinstance(sources, dict):
            ret_val = {}
            for key,val in sources.items():
                match (val.get("DB_TYPE", "").upper()):
                    case "BIGQUERY" | "FIREBASE":
                        ret_val[key] = BigQuerySchema(name=key, all_elements=val)
                    case "MYSQL":
                        ret_val[key] = MySQLSchema(name=key, all_elements=val)
                    case "FILE":
                        ret_val[key] = FileHostConfig(name=key, all_elements=val)
                    case _:
                        Logger.Log(f"Game source {key} did not  have a valid 'DB_TYPE' (value: {val.get('DB_TYPE', '')}), and will be skipped!", logging.WARN)
        else:
            ret_val = {}
            Logger.Log(f"Config data sources was unexpected type {type(sources)}, defaulting to empty dict: {ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseGameSourceMap(map, sources) -> Dict[str, GameSourceSchema]:
        ret_val : Dict[str, GameSourceSchema]
        if isinstance(map, dict):
            ret_val = { key : GameSourceSchema(name=key, all_elements=val, data_sources=sources) for key, val in map.items() }
        else:
            ret_val = {}
            Logger.Log(f"Config game source map was unexpected type {type(map)}, defaulting to empty dict: {ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseGameDestMap(map, sources) -> Dict[str, GameSourceSchema]:
        ret_val : Dict[str, GameSourceSchema]
        if isinstance(map, dict):
            ret_val = { key : GameSourceSchema(name=key, all_elements=val, data_sources=sources) for key, val in map.items() }
        else:
            ret_val = {}
            Logger.Log(f"Config game source map was unexpected type {type(map)}, defaulting to empty dict: {ret_val}.", logging.WARN)
        return ret_val