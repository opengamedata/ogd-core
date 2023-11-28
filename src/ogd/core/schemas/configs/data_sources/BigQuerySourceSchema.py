# import standard libraries
import abc
import logging
from typing import Any, Dict, Optional, Type
# import local files
from ogd.core.schemas.Schema import Schema
from ogd.core.schemas.configs.data_sources.DataSourceSchema import DataSourceSchema
from ogd.core.utils.Logger import Logger

class BigQuerySchema(DataSourceSchema):
    def __init__(self, name:str, all_elements:Dict[str, Any], fallbacks:Dict[str, Any]={}):
        self._project_id : str
        self._credential : Optional[str]

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} Game Source config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        if "PROJECT_ID" in all_elements.keys():
            self._project_id = BigQuerySchema._parseProjectID(all_elements["PROJECT_ID"])
        elif "PROJECT_ID" in fallbacks.keys():
            self._project_id = BigQuerySchema._parseProjectID(fallbacks["PROJECT_ID"])
        else:
            self._project_id = "UNKNOWN"
            Logger.Log(f"{name} config does not have a 'DATASET_ID' element; defaulting to dataset_id={self._project_id}", logging.WARN)
        if "PROJECT_KEY" in all_elements.keys():
            self._credential = BigQuerySchema._parseCredential(all_elements["PROJECT_KEY"])
        elif "PROJECT_KEY" in fallbacks.keys():
            self._credential = BigQuerySchema._parseCredential(fallbacks["PROJECT_KEY"])
        else:
            self._credential = None
            Logger.Log(f"{name} config does not have a 'PROJECT_KEY' element; defaulting to credential=None", logging.WARN)

        _used = {"PROJECT_ID", "DATASET_ID", "PROJECT_KEY"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def ProjectID(self) -> str:
        return self._project_id

    @property
    def Credential(self) -> Optional[str]:
        return self._credential

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: `{self.AsConnectionInfo}` ({self.Type})"
        return ret_val

    @property
    def AsConnectionInfo(self) -> str:
        ret_val : str = f"{self.ProjectID}"
        return ret_val

    @staticmethod
    def _parseProjectID(project_id) -> str:
        ret_val : str
        if isinstance(project_id, str):
            ret_val = project_id
        else:
            ret_val = str(project_id)
            Logger.Log(f"Data Source project ID was unexpected type {type(project_id)}, defaulting to str(project_id)={ret_val}.", logging.WARN)
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
