# import standard libraries
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Self
# import local files
from ogd.common.configs.storage.RepositoryIndexingConfig import RepositoryIndexingConfig
from ogd.common.configs.GameStoreConfig import GameStoreConfig
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.configs.storage.BigQueryConfig import BigQueryConfig
from ogd.common.configs.storage.FileStoreConfig import FileStoreConfig
from ogd.common.configs.storage.MySQLConfig import MySQLConfig
from ogd.common.schemas.Schema import Schema
from ogd.common.schemas.tables.EventTableSchema import EventTableSchema
from ogd.common.schemas.tables.FeatureTableSchema import FeatureTableSchema
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class CoreConfig(Schema):
    """Dumb struct containing properties for each standard OGD-core config item.
    """
    _DEFAULT_LOG_FILE = False
    _DEFAULT_BATCH_SIZE = 500
    _DEFAULT_DBG_STR = "INFO"
    _DEFAULT_DBG = logging.INFO
    _DEFAULT_FAIL_FAST = False
    _DEFAULT_WITH_PROFILING = False
    _DEFAULT_FILE_IDX = RepositoryIndexingConfig.Default()
    _DEFAULT_DATA_SRC = {}
    _DEFAULT_GAME_SRC_MAP = {}

    def __init__(
        self,
        name: str,
        log_file: Optional[bool],
        batch_size: Optional[int],
        dbg_level: Optional[int],
        fail_fast: Optional[bool],
        with_profiling: Optional[bool],
        file_idx: Optional[RepositoryIndexingConfig],
        data_src: Optional[Dict[str, DataStoreConfig]],
        game_src_map: Optional[Dict[str, GameStoreConfig]],
        other_elements: Dict[str, Any]
    ):
        """Constructs a CoreConfig, from a name and dictionary of JSON-style elements.

        :param name: The name of the configuration schema.
        :type name: str
        :param all_elements: A dictionary mapping config item names to their configured values. These will be checked and made available through the CoreConfig properties.
        :type all_elements: Dict[str, Any]
        """
        unparsed_elements : Map = other_elements or {}

        self._log_file       : bool               = log_file       or self._parseLogFile(unparsed_elements=unparsed_elements, schema_name=name)
        self._batch_size     : int                = batch_size     or self._parseBatchSize(unparsed_elements=unparsed_elements, schema_name=name)
        self._dbg_level      : int                = dbg_level      or self._parseDebugLevel(unparsed_elements=unparsed_elements, schema_name=name)
        self._fail_fast      : bool               = fail_fast      or self._parseFailFast(unparsed_elements=unparsed_elements, schema_name=name)
        self._with_profiling : bool               = with_profiling or self._parseProfiling(unparsed_elements=unparsed_elements, schema_name=name)
        self._file_idx       : RepositoryIndexingConfig   = file_idx       or self._parseFileIndexing(unparsed_elements=unparsed_elements, schema_name=name)
        self._data_src       : Dict[str, DataStoreConfig] = data_src or self._parseDataSources(unparsed_elements=unparsed_elements, schema_name=name)
        self._game_src_map   : Dict[str, GameStoreConfig] = game_src_map or self._parseGameSourceMap(unparsed_elements=unparsed_elements, schema_name=name)
        
        # Set up data store configs and table schemas for each game source mapping
        for game, cfg in self._game_src_map.items():
            _store = self._data_src.get(cfg.StoreName)
            if _store:
                cfg.StoreConfig = _store
            cfg.Table = EventTableSchema.FromFile(schema_name=cfg.TableSchemaName)
            

        super().__init__(name=name, other_elements=unparsed_elements)

    @property
    def DataDirectory(self) -> Path:
        """
        The local directory where export files will be stored by default.

        :return: The local directory where export files will be stored by default.
        :rtype: Path
        """
        return self.FileIndexConfig.LocalDirectory.FolderPath

    @property
    def UseLogFile(self) -> bool:
        """
        Whether to use a log file to store log output from exports.
        """
        return self._log_file

    @property
    def BatchSize(self) -> int:
        """
        The number of sessions to process at once during an export.
        """
        return self._batch_size

    @property
    def DebugLevel(self) -> int:
        """
        The least-severe level of debug output that should be logged.
        Defaults to INFO if not specified.
        """
        return self._dbg_level

    @property
    def FailFast(self) -> bool:
        """
        Whether to fail the export on errors due to bad data, or ignore the bad data and continue processing.
        """
        return self._fail_fast

    @property
    def WithProfiling(self) -> bool:
        """
        Whether to track and include profiling data in the output or not.
        """
        return self._with_profiling

    @property
    def FileIndexConfig(self) -> RepositoryIndexingConfig:
        """
        A collection of settings for indexing output files.

        TODO : Need better documentation of this item.
        """
        return self._file_idx

    @property
    def DataSources(self) -> Dict[str, DataStoreConfig]:
        """
        A collection of all configured sources of data that can be used for exports.
        """
        return self._data_src

    @property
    def GameSourceMap(self) -> Dict[str, GameStoreConfig]:
        """
        A mapping from game IDs to the data sources they use.
        """
        return self._game_src_map

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        """
        A Markdown-formatted stringification of the CoreConfig.
        (presently just the schema name)
        """
        ret_val : str

        ret_val = f"{self.Name}"
        return ret_val

    @classmethod
    def Default(cls) -> "CoreConfig":
        return CoreConfig(
            name="DefaultCoreConfig",
            log_file=cls._DEFAULT_LOG_FILE,
            batch_size=cls._DEFAULT_BATCH_SIZE,
            dbg_level=cls._DEFAULT_DBG,
            fail_fast=cls._DEFAULT_FAIL_FAST,
            with_profiling=cls._DEFAULT_WITH_PROFILING,
            file_idx=cls._DEFAULT_FILE_IDX,
            data_src=cls._DEFAULT_DATA_SRC,
            game_src_map=cls._DEFAULT_GAME_SRC_MAP,
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None, default_override:Optional[Self]=None)-> "CoreConfig":
        return CoreConfig(name=name, log_file=None, batch_size=None, dbg_level=None, fail_fast=None, with_profiling=None,
                          file_idx=None, data_src=None, game_src_map=None, other_elements=unparsed_elements)

    @staticmethod
    def _parseLogFile(unparsed_elements:Map, schema_name:Optional[str]=None) -> bool:
        return CoreConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=['LOG_FILE'],
            to_type=bool,
            default_value=CoreConfig._DEFAULT_LOG_FILE,
            remove_target=True,
            schema_name=schema_name
        )

    @staticmethod
    def _parseBatchSize(unparsed_elements:Map, schema_name:Optional[str]=None) -> int:
        return CoreConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=['BATCH_SIZE'],
            to_type=int,
            default_value=CoreConfig._DEFAULT_BATCH_SIZE,
            remove_target=True,
            schema_name=schema_name
        )

    @staticmethod
    def _parseDebugLevel(unparsed_elements:Map, schema_name:Optional[str]=None) -> int:
        ret_val : int
        raw_level : str = CoreConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=['DEBUG_LEVEL'],
            to_type=str,
            default_value=CoreConfig._DEFAULT_DBG_STR,
            remove_target=True,
            schema_name=schema_name
        )
        match raw_level.upper():
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
                Logger.Log(f"Config debug level had unexpected value {raw_level}, defaulting to logging.INFO.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseFailFast(unparsed_elements:Map, schema_name:Optional[str]=None) -> bool:
        return CoreConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=['FAIL_FAST'],
            to_type=bool,
            default_value=CoreConfig._DEFAULT_FAIL_FAST,
            remove_target=True,
            schema_name=schema_name
        )

    @staticmethod
    def _parseProfiling(unparsed_elements:Map, schema_name:Optional[str]=None) -> bool:
        return CoreConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=['WITH_PROFILING'],
            to_type=bool,
            default_value=CoreConfig._DEFAULT_FAIL_FAST,
            remove_target=True,
            schema_name=schema_name
        )

    @staticmethod
    def _parseFileIndexing(unparsed_elements:Map, schema_name:Optional[str]=None) -> RepositoryIndexingConfig:
        ret_val : RepositoryIndexingConfig

        raw_indexing = CoreConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=['REPOSITORY_CONFIG', 'FILE_INDEXING'],
            to_type=dict,
            default_value=None,
            remove_target=True,
            schema_name=schema_name
        )

        if isinstance(raw_indexing, dict):
            ret_val = RepositoryIndexingConfig.FromDict(name="FILE_INDEXING", unparsed_elements=raw_indexing)
        else:
            ret_val = CoreConfig._DEFAULT_FILE_IDX
            Logger.Log(f"Config file indexing was not found, defaulting to default indexing config: {ret_val.AsMarkdown}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDataSources(unparsed_elements:Map, schema_name:Optional[str]=None) -> Dict[str, DataStoreConfig]:
        ret_val : Dict[str, DataStoreConfig]

        raw_sources = CoreConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=['DATA_SOURCES', 'GAME_SOURCES'],
            to_type=dict,
            default_value=None,
            remove_target=True,
            schema_name=schema_name
        )
        if isinstance(raw_sources, dict):
            ret_val = {}
            for key,val in raw_sources.items():
                src_type = val.get("SOURCE_TYPE", val.get("DB_TYPE", "UNKNOWN")).upper()
                match src_type:
                    case "BIGQUERY" | "FIREBASE":
                        ret_val[key] = BigQueryConfig.FromDict(name=key, unparsed_elements=val)
                    case "MYSQL":
                        ret_val[key] = MySQLConfig.FromDict(name=key, unparsed_elements=val)
                    case "FILE":
                        ret_val[key] = FileStoreConfig.FromDict(name=key, unparsed_elements=val)
                    case _:
                        Logger.Log(f"Game source {key} did not  have a valid 'DB_TYPE' (value: {val.get('DB_TYPE', '')}), and will be skipped!", logging.WARN)
        else:
            ret_val = CoreConfig._DEFAULT_DATA_SRC
            Logger.Log(f"Config data sources was not found, defaulting to {ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseGameSourceMap(unparsed_elements:Map, schema_name:Optional[str]=None) -> Dict[str, GameStoreConfig]:
        ret_val : Dict[str, GameStoreConfig]

        raw_mappings = CoreConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=['GAME_SOURCE_MAP'],
            to_type=dict,
            default_value=None,
            remove_target=True,
            schema_name=schema_name
        )
        if isinstance(raw_mappings, dict):
            ret_val = { key : GameStoreConfig.FromDict(name=key, unparsed_elements=val) for key, val in raw_mappings.items() }
        else:
            ret_val = {}
            Logger.Log(f"Config game source map was not found, defaulting to: {ret_val}.", logging.WARN)
        return ret_val
