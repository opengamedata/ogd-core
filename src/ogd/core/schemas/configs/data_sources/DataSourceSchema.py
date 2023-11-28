# import standard libraries
import abc
import logging
from typing import Any, Dict
# import local files
from ogd.core.schemas.Schema import Schema
from ogd.core.utils.Logger import Logger

class DataSourceSchema(Schema):
    def __init__(self, name:str, other_elements:Dict[str, Any]):
        self._db_type : str
        if not isinstance(other_elements, dict):
            other_elements = {}
            Logger.Log(f"For {name} Data Source config, other_elements was not a dict, defaulting to empty dict", logging.WARN)
        # Parse DB info
        if "DB_TYPE" in other_elements.keys():
            self._db_type = DataSourceSchema._parseDBType(other_elements["DB_TYPE"])
        else:
            self._db_type = "UNKNOWN"
            Logger.Log(f"{name} config does not have a 'DB_TYPE' element; defaulting to db_host={self._db_type}", logging.WARN)

        _used = {"DB_TYPE"}
        _leftovers = { key : val for key,val in other_elements.items() if key not in _used }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def Type(self) -> str:
        """The type of source indicated by the data source schema.

        This includes but is not limited to "FIREBASE", "BIGQUERY", and "MySQL"

        :return: A string describing the type of the data source
        :rtype: str
        """
        return self._db_type

    @property
    @abc.abstractmethod
    def AsConnectionInfo(self) -> str:
        pass

    @staticmethod
    def _parseDBType(db_type) -> str:
        ret_val : str
        if isinstance(db_type, str):
            ret_val = db_type
        else:
            ret_val = str(db_type)
            Logger.Log(f"Data Source DB type was unexpected type {type(db_type)}, defaulting to str(db_type)={ret_val}.", logging.WARN)
        return ret_val
