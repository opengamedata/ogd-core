# import standard libraries
import abc
import logging
from typing import Any, Dict, Optional, Type
# import local files
from schemas.Schema import Schema
from utils import Logger

class DataSourceSchema(Schema):
    def __init__(self, name:str, other_elements:Dict[str, Any]):
        super().__init__(name=name, other_elements=other_elements)

    @property
    @abc.abstractmethod
    def Type(self) -> str:
        pass

class BigQuerySchema(DataSourceSchema):
    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._project_id : str
        self._dataset_id : str
        self._credential : Optional[str]

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} Game Source config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        if "PROJECT_ID" in all_elements.keys():
            self._project_id = BigQuerySchema._parseProjectID(all_elements["PROJECT_ID"])
        else:
            self._project_id = "UNKNOWN"
            Logger.Log(f"{name} config does not have a 'PROJECT_ID' element; defaulting to project_id={self._project_id}", logging.WARN)
        if "DATASET_ID" in all_elements.keys():
            self._dataset_id = BigQuerySchema._parseDatasetID(all_elements["DATASET_ID"])
        else:
            self._dataset_id = "UNKNOWN"
            Logger.Log(f"{name} config does not have a 'DATASET_ID' element; defaulting to dataset_id={self._dataset_id}", logging.WARN)
        if "PROJECT_KEY" in all_elements.keys():
            self._credential = BigQuerySchema._parseCredential(all_elements["PROJECT_KEY"])
        else:
            self._credential = None
            Logger.Log(f"{name} config does not have a 'PROJECT_KEY' element; defaulting to credential=None", logging.WARN)

        _used = {"PROJECT_ID", "DATASET_ID", "PROJECT_KEY"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def Type(self) -> str:
        return "BigQuery"

    @property
    def ProjectID(self) -> str:
        return self._project_id

    @property
    def DatasetID(self) -> str:
        return self._dataset_id

    @property
    def Credential(self) -> Optional[str]:
        return self._credential

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: `{self.ProjectID}.{self.DatasetID}` ({self.Type})"
        return ret_val

    @staticmethod
    def _parseProjectID(proj_id) -> str:
        ret_val : str
        if isinstance(proj_id, str):
            ret_val = proj_id
        else:
            ret_val = str(proj_id)
            Logger.Log(f"Data Source project ID was unexpected type {type(proj_id)}, defaulting to str(proj_id)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDatasetID(data_id) -> str:
        ret_val : str
        if isinstance(data_id, str):
            ret_val = data_id
        else:
            ret_val = str(data_id)
            Logger.Log(f"Data Source dataset ID was unexpected type {type(data_id)}, defaulting to str(data_id)={ret_val}.", logging.WARN)
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

class MySQLSchema(DataSourceSchema):
    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._project_id : str
        self._dataset_id : str
        self._credential : Optional[str]

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} Game Source config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        if "PROJECT_ID" in all_elements.keys():
            self._project_id = BigQuerySchema._parseProjectID(all_elements["PROJECT_ID"])
        else:
            self._project_id = "UNKNOWN"
            Logger.Log(f"{name} config does not have a 'PROJECT_ID' element; defaulting to project_id={self._project_id}", logging.WARN)
        if "DATASET_ID" in all_elements.keys():
            self._dataset_id = BigQuerySchema._parseDatasetID(all_elements["DATASET_ID"])
        else:
            self._dataset_id = "UNKNOWN"
            Logger.Log(f"{name} config does not have a 'DATASET_ID' element; defaulting to dataset_id={self._dataset_id}", logging.WARN)
        if "PROJECT_KEY" in all_elements.keys():
            self._credential = BigQuerySchema._parseCredential(all_elements["PROJECT_KEY"])
        else:
            self._credential = None
            Logger.Log(f"{name} config does not have a 'PROJECT_KEY' element; defaulting to credential=None", logging.WARN)

        _used = {"PROJECT_ID", "DATASET_ID", "PROJECT_KEY"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def Type(self) -> str:
        return "BigQuery"

    @property
    def ProjectID(self) -> str:
        return self._project_id

    @property
    def DatasetID(self) -> str:
        return self._dataset_id

    @property
    def Credential(self) -> Optional[str]:
        return self._credential

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: `{self.ProjectID}.{self.DatasetID}` ({self.Type})"
        return ret_val

    @staticmethod
    def _parseProjectID(proj_id) -> str:
        ret_val : str
        if isinstance(proj_id, str):
            ret_val = proj_id
        else:
            ret_val = str(proj_id)
            Logger.Log(f"Data Source project ID was unexpected type {type(proj_id)}, defaulting to str(proj_id)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDatasetID(data_id) -> str:
        ret_val : str
        if isinstance(data_id, str):
            ret_val = data_id
        else:
            ret_val = str(data_id)
            Logger.Log(f"Data Source dataset ID was unexpected type {type(data_id)}, defaulting to str(data_id)={ret_val}.", logging.WARN)
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

def ParseSourceType(all_elements:Dict[str, Any]) -> Optional[Type[DataSourceSchema]]:
    match (all_elements.get("DB_TYPE", "").upper()):
        case "BIGQUERY":
            return BigQuerySchema
        case "MYSQL":
            return MySQLSchema
        case _:
            return None
