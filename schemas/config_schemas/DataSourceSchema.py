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
        self._db_host  : str
        self._db_port  : int
        self._db_name  : str
        self._db_user  : str
        self._db_pass  : Optional[str]
        self._ssh_host : Optional[str]
        self._ssh_port : Optional[int]
        self._ssh_user : Optional[str]
        self._ssh_pass : Optional[str]

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} MySQL Data Source config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        # Parse DB info
        if "DB_HOST" in all_elements.keys():
            self._db_host = MySQLSchema._parseDBHost(all_elements["DB_HOST"])
        else:
            self._db_host = "UNKNOWN"
            Logger.Log(f"{name} config does not have a 'DB_HOST' element; defaulting to db_host={self._db_host}", logging.WARN)
        if "DB_PORT" in all_elements.keys():
            self._db_port = MySQLSchema._parseDBPort(all_elements["DB_PORT"])
        else:
            self._db_port = 3306
            Logger.Log(f"{name} config does not have a 'DB_PORT' element; defaulting to db_port={self._db_port}", logging.WARN)
        if "DB_NAME" in all_elements.keys():
            self._db_name = MySQLSchema._parseDBName(all_elements["DB_NAME"])
        else:
            self._db_name = name
            Logger.Log(f"{name} config does not have a 'DB_NAME' element; defaulting to db_name={self._db_name}", logging.WARN)
        if "DB_USER" in all_elements.keys():
            self._db_user = MySQLSchema._parseDBUser(all_elements["DB_USER"])
        else:
            self._db_user = "UNKOWN"
            Logger.Log(f"{name} config does not have a 'DB_USER' element; defaulting to db_user={self._db_user}", logging.WARN)
        if "DB_PW" in all_elements.keys():
            self._db_pass = MySQLSchema._parseDBPass(all_elements["DB_PW"])
        else:
            self._db_pass = None
            Logger.Log(f"{name} config does not have a 'DB_PW' element; defaulting to db_pass=None", logging.WARN)
        # Parse SSH info, if it exists. Don't notify, if it doesn't exist.
        if "SSH_HOST" in all_elements.keys():
            self._ssh_host = MySQLSchema._parseSSHHost(all_elements["SSH_HOST"])
        else:
            self._ssh_host = None
        if "SSH_PORT" in all_elements.keys():
            self._ssh_port = MySQLSchema._parseSSHPort(all_elements["SSH_PORT"])
        else:
            self._ssh_port = None
        if "SSH_USER" in all_elements.keys():
            self._ssh_user = MySQLSchema._parseSSHUser(all_elements["SSH_USER"])
        else:
            self._ssh_user = None
        if "SSH_PW" in all_elements.keys():
            self._ssh_pass = MySQLSchema._parseSSHPass(all_elements["SSH_PW"])
        else:
            self._ssh_pass = None

        _used = {"DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PW", "SSH_HOST", "SSH_PORT", "SSH_USER", "SSH_PW"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def Type(self) -> str:
        return "BigQuery"

    @property
    def DBHost(self) -> str:
        return self._db_host

    @property
    def DBPort(self) -> int:
        return self._db_port

    @property
    def DBName(self) -> str:
        return self._db_name

    @property
    def DBUser(self) -> str:
        return self._db_user

    @property
    def DBPass(self) -> Optional[str]:
        return self._db_pass

    @property
    def SSHHost(self) -> Optional[str]:
        return self._ssh_host

    @property
    def SSHPort(self) -> Optional[int]:
        return self._ssh_port

    @property
    def SSHUser(self) -> Optional[str]:
        return self._ssh_user

    @property
    def SSHPass(self) -> Optional[str]:
        return self._ssh_pass

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ssh_part = f"{self.SSHUser}@{self.SSHHost}:{self.SSHPort} -> " if (self.SSHHost and self.SSHPort and self.SSHUser) else ""
        ret_val = f"{self.Name}: `{ssh_part}{self.DBUser}@{self.DBHost}:{self.DBPort}/{self.DBName}` ({self.Type})"
        return ret_val

    @staticmethod
    def _parseDBHost(db_host) -> str:
        ret_val : str
        if isinstance(db_host, str):
            ret_val = db_host
        else:
            ret_val = str(db_host)
            Logger.Log(f"MySQL Data Source DB host was unexpected type {type(db_host)}, defaulting to str(db_host)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDBPort(db_port) -> int:
        ret_val : int
        if isinstance(db_port, int):
            ret_val = db_port
        else:
            ret_val = int(db_port)
            Logger.Log(f"MySQL Data Source DB port was unexpected type {type(db_port)}, defaulting to int(db_port)={ret_val}.", logging.WARN)
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
    def _parseDBUser(db_user) -> str:
        ret_val : str
        if isinstance(db_user, str):
            ret_val = db_user
        else:
            ret_val = str(db_user)
            Logger.Log(f"MySQL Data Source DB username was unexpected type {type(db_user)}, defaulting to str(db_user)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDBPass(db_pass) -> str:
        ret_val : str
        if isinstance(db_pass, str):
            ret_val = db_pass
        else:
            ret_val = str(db_pass)
            Logger.Log(f"MySQL Data Source DB password was unexpected type, defaulting to str(db_pass)=***.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseSSHHost(ssh_host) -> str:
        ret_val : str
        if isinstance(ssh_host, str):
            ret_val = ssh_host
        else:
            ret_val = str(ssh_host)
            Logger.Log(f"MySQL Data Source SSH host was unexpected type {type(ssh_host)}, defaulting to str(ssh_host)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseSSHPort(ssh_port) -> int:
        ret_val : int
        if isinstance(ssh_port, int):
            ret_val = ssh_port
        else:
            ret_val = int(ssh_port)
            Logger.Log(f"MySQL Data Source SSH port was unexpected type {type(ssh_port)}, defaulting to int(ssh_port)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseSSHUser(ssh_user) -> str:
        ret_val : str
        if isinstance(ssh_user, str):
            ret_val = ssh_user
        else:
            ret_val = str(ssh_user)
            Logger.Log(f"MySQL Data Source SSH username was unexpected type {type(ssh_user)}, defaulting to str(ssh_user)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseSSHPass(ssh_pass) -> str:
        ret_val : str
        if isinstance(ssh_pass, str):
            ret_val = ssh_pass
        else:
            ret_val = str(ssh_pass)
            Logger.Log(f"MySQL Data Source SSH password was unexpected type, defaulting to str(ssh_pass)=***.", logging.WARN)
        return ret_val

def ParseSourceType(all_elements:Dict[str, Any]) -> Optional[Type[DataSourceSchema]]:
    match (all_elements.get("DB_TYPE", "").upper()):
        case "BIGQUERY":
            return BigQuerySchema
        case "MYSQL":
            return MySQLSchema
        case _:
            return None
