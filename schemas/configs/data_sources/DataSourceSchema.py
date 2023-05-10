# import standard libraries
import abc
import logging
from typing import Any, Dict
# import local files
from schemas.Schema import Schema
from utils import Logger

class DataSourceSchema(Schema):
    def __init__(self, name:str, other_elements:Dict[str, Any]):
        self._db_type : str
        self._db_name  : str
        if not isinstance(other_elements, dict):
            other_elements = {}
            Logger.Log(f"For {name} Data Source config, other_elements was not a dict, defaulting to empty dict", logging.WARN)
        # Parse DB info
        if "DB_TYPE" in other_elements.keys():
            self._db_type = DataSourceSchema._parseDBType(other_elements["DB_TYPE"])
        else:
            self._db_type = "UNKNOWN"
            Logger.Log(f"{name} config does not have a 'DB_TYPE' element; defaulting to db_host={self._db_type}", logging.WARN)
        if "DB_NAME" in other_elements.keys():
            self._db_name = DataSourceSchema._parseDBName(other_elements["DB_NAME"])
        else:
            self._db_name = name
            Logger.Log(f"{name} config does not have a 'DB_NAME' element; defaulting to db_name={self._db_name}", logging.WARN)

        _used = {"DB_TYPE"}
        _leftovers = { key : val for key,val in other_elements.items() if key not in _used }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def Type(self) -> str:
        return self._db_type

    @property
    def DBName(self) -> str:
        return self._db_name

    @staticmethod
    def _parseDBType(db_type) -> str:
        ret_val : str
        if isinstance(db_type, str):
            ret_val = db_type
        else:
            ret_val = str(db_type)
            Logger.Log(f"Data Source DB type was unexpected type {type(db_type)}, defaulting to str(db_type)={ret_val}.", logging.WARN)
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
