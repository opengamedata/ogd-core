# import standard libraries
import logging
from typing import Any, Dict, List, Optional, Union
# import local files
from schemas.data_sources.DataHostConfig import DataHostConfig
from schemas.Schema import Schema
from utils.Logger import Logger

class GameSourceSchema(Schema):
    def __init__(self, name:str, all_elements:Dict[str, Any], data_sources:Dict[str, DataHostConfig]):
        self._host_cfg_name : str
        self._data_host     : Optional[DataHostConfig]
        self._db_name       : str
        self._table_schema  : str
        self._table_name    : str

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} Game Source config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        if "source" in all_elements.keys():
            self._host_cfg_name = GameSourceSchema._parseSource(all_elements["source"])
        else:
            self._host_cfg_name = "UNKNOWN"
            Logger.Log(f"{name} config does not have a 'source' element; defaulting to source_name={self._host_cfg_name}", logging.WARN)
        if self._host_cfg_name in data_sources.keys():
            self._data_host = data_sources[self._host_cfg_name]
        else:
            self._data_host = None
            Logger.Log(f"{name} config's 'source' name ({self._host_cfg_name}) was not found in available source schemas; defaulting to source_schema={self._data_host}", logging.WARN)
        if "database" in all_elements.keys():
            self._db_name = GameSourceSchema._parseDBName(all_elements["database"])
        else:
            self._db_name = name
            Logger.Log(f"{name} config does not have a 'database' element; defaulting to db_name={self._db_name}", logging.WARN)
        if "table" in all_elements.keys():
            self._table_name = GameSourceSchema._parseTableName(all_elements["table"])
        else:
            self._table_name = "UNKNOWN"
            Logger.Log(f"{name} config does not have a 'table' element; defaulting to table={self._table_name}", logging.WARN)
        if "schema" in all_elements.keys():
            self._schema = GameSourceSchema._parseSchema(all_elements["schema"])
        else:
            self._schema = "UNKNOWN"
            Logger.Log(f"{name} config does not have a 'schema' element; defaulting to schema={self._schema}", logging.WARN)

        _used = {"source", "database", "table", "schema"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def DataHostName(self) -> str:
        return self._host_cfg_name

    @property
    def DataHost(self) -> Optional[DataHostConfig]:
        return self._data_host

    @property
    def DatabaseName(self) -> str:
        return self._db_name

    @property
    def TableName(self) -> str:
        return self._table_name

    @property
    def EventTableSchema(self) -> str:
        return self._schema

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: _{self.EventTableSchema}_ format, source {self.DataHost.Name if self.DataHost else 'None'} : {self.DatabaseName}.{self.TableName}"
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
    def _parseDBName(db_name) -> str:
        ret_val : str
        if isinstance(db_name, str):
            ret_val = db_name
        else:
            ret_val = str(db_name)
            Logger.Log(f"MySQL Data Source DB name was unexpected type {type(db_name)}, defaulting to str(db_name)={ret_val}.", logging.WARN)
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
