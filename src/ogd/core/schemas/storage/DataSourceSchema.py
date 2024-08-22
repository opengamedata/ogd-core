# import standard libraries
import abc
import logging
from pathlib import Path
from typing import Any, Dict # , overload
# import local files
from ogd.core.schemas.Schema import Schema
from ogd.core.schemas.storage.CredentialSchema import CredentialSchema
from ogd.core.utils.Logger import Logger


class DataSourceSchema(Schema):
    """Dumb struct to contain data pertaining to a data source, which a StorageConnector can connect to.

    Every source has:
    - A named "type" to inform what StorageConnector should be instantiated
    - A config "name" for use within ogd software for identifying a particular data source config
    - A resource "location" for use by the StorageConnector (such as a filename, cloud project name, or database host)
    """
    # @overload
    # def __init__(self, name:str, other_elements:Dict[str, Any]): ...

    def __init__(self, name:str, unparsed_elements:Dict[str, Any] | Any):
        self._source_type : str
        # 1. Ensure we've actually got a dict to parse from
        if not isinstance(unparsed_elements, dict):
            unparsed_elements = {}
            Logger.Log(f"For {name} Data Source config, other_elements was not a dict, defaulting to empty dict", logging.WARN)
        # 2. Parse standard elements
        if "SOURCE_TYPE" in unparsed_elements.keys():
            self._source_type = DataSourceSchema._parseSourceType(unparsed_elements["SOURCE_TYPE"])
        else:
            self._source_type = "UNKNOWN"
            Logger.Log(f"{name} config does not have a 'database' element; defaulting to db_name={self._db_name}", logging.WARN)

        # 3. Parse legacy naming of standard elements
        #    * DB_TYPE -> SOURCE_TYPE
        if "DB_TYPE" in unparsed_elements.keys() and "SOURCE_TYPE" not in unparsed_elements.keys():
            self._source_type = DataSourceSchema._parseSourceType(unparsed_elements["DB_TYPE"])
        else:
            self._db_type = "UNKNOWN"
            Logger.Log(f"{name} config does not have a 'DB_TYPE' element; defaulting to db_host={self._db_type}", logging.WARN)

        _used = {"SOURCE_TYPE", "DB_TYPE"}
        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
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
    def Location(self) -> str | Path:
        pass

    @property
    @abc.abstractmethod
    def Credential(self) -> CredentialSchema:
        pass

    @property
    @abc.abstractmethod
    def AsConnectionInfo(self) -> str:
        pass

    @staticmethod
    def _parseSourceType(source_type) -> str:
        ret_val : str
        if isinstance(source_type, str):
            ret_val = source_type
        else:
            ret_val = str(source_type)
            Logger.Log(f"Data Source typename was unexpected type {type(source_type)}, defaulting to str(source_type)={ret_val}.", logging.WARN)
        return ret_val
