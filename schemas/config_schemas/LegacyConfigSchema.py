# import standard libraries
import logging
from pathlib import Path
from typing import Any, Dict, Optional
# import local files
from schemas.config_schemas.IndexingSchema import FileIndexingSchema
from schemas.config_schemas.SSHSchema import SSHSchema
from schemas.config_schemas.GameSourceSchema import GameSourceMapElementSchema
from schemas.config_schemas.DataSourceSchema import DataSourceSchema, BigQuerySchema, MySQLSchema, ParseSourceType
from schemas.Schema import Schema
from utils import Logger

class LegacyConfigSchema(Schema):
    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._data_dir   : Path
        self._ssh_config : SSHSchema

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} base config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        if "DATA_DIR" in all_elements.keys():
            self._data_dir = LegacyConfigSchema._parseDataDir(all_elements["DATA_DIR"])
        else:
            self._data_dir = Path("./data/")
            # No need to warn if outdated DATA_DIR does not exist.
            # Logger.Log(f"{name} config does not have a 'DATA_DIR' element; defaulting to data_dir={self._data_dir}", logging.WARN)
        if "SSH_CONFIG" in all_elements.keys():
            self._ssh_config = LegacyConfigSchema._parseSSHConfig(all_elements["SSH_CONFIG"])
        else:
            self._ssh_config = SSHSchema(name="SSH_CONFIG", all_elements={})
            Logger.Log(f"{name} config does not have a 'SSH_CONFIG' element; defaulting to ssh_config={self._ssh_config}", logging.WARN)

        _used = {"DATA_DIR", "SSH_CONFIG"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def DataDirectory(self) -> Path:
        return self._data_dir

    @property
    def SSHConfig(self) -> SSHSchema:
        return self._ssh_config

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
    def _parseSSHConfig(ssh) -> SSHSchema:
        ret_val : SSHSchema
        if isinstance(ssh, dict):
            ret_val = SSHSchema(name="SSH_CONFIG", all_elements=ssh)
        else:
            ret_val = SSHSchema(name="SSH_CONFIG", all_elements={})
            Logger.Log(f"Config ssh config was unexpected type {type(ssh)}, defaulting to default ssh config: {ret_val.AsMarkdown}.", logging.WARN)
        return ret_val