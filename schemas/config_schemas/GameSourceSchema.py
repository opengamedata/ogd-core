# import standard libraries
import logging
from typing import Any, Dict, List, Optional, Union
# import local files
from schemas.Schema import Schema
from utils import Logger

class GameSourceSchema(Schema):
    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._schema     : str
        self._source     : str
        self._table_name : str
        self._credential : Optional[str]

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} Game Source config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        if "schema" in all_elements.keys():
            self._schema = GameSourceSchema._parseSchema(all_elements["schema"])
        else:
            self._schema = "UNKNOWN"
            Logger.Log(f"{name} config does not have a 'schema' element; defaulting to schema={self._schema}", logging.WARN)
        if "source" in all_elements.keys():
            self._source = GameSourceSchema._parseSource(all_elements["source"])
        else:
            self._source = "UNKNOWN"
            Logger.Log(f"{name} config does not have a 'source' element; defaulting to source={self._source}", logging.WARN)
        if "table" in all_elements.keys():
            self._table_name = GameSourceSchema._parseTableName(all_elements["table"])
        else:
            self._table_name = "UNKNOWN"
            Logger.Log(f"{name} config does not have a 'table' element; defaulting to table={self._table_name}", logging.WARN)
        if "credential" in all_elements.keys():
            self._credential = GameSourceSchema._parseCredential(all_elements["credential"])
        else:
            self._credential = None
            Logger.Log(f"{name} config does not have a 'credential' element; defaulting to credential={self._credential}", logging.WARN)

        _used = {"schema", "source", "table", "credential"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def Schema(self) -> str:
        return self._schema

    @property
    def Source(self) -> str:
        return self._source

    @property
    def TableName(self) -> str:
        return self._table_name

    @property
    def Credential(self) -> Optional[str]:
        return self._credential

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: _{self.Schema}_ format, source {self.Source}.{self.TableName}"
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