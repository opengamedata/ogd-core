# import standard libraries
import logging
from typing import Any, Dict, Optional, Type
# import local files
from ogd.core.schemas.Schema import Schema
from ogd.core.schemas.configs.data_sources.DataSourceSchema import DataSourceSchema
from ogd.core.utils.Logger import Logger

class SSHSchema(Schema):
    def __init__(self, name:str, all_elements:Dict[str, Any], fallbacks:Dict[str, Any]={}):
        self._host : Optional[str]
        self._user : Optional[str]
        self._pass : Optional[str]
        self._port : int

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} base config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        if "SSH_HOST" in all_elements.keys():
            self._host = SSHSchema._parseHost(all_elements["SSH_HOST"])
        elif "SSH_HOST" in fallbacks.keys():
            self._host = SSHSchema._parseHost(fallbacks["SSH_HOST"])
        else:
            self._host = None
            Logger.Log(f"{name} config does not have a 'SSH_HOST' element; defaulting to ssh_host={self._host}", logging.WARN)
        if "SSH_USER" in all_elements.keys():
            self._user = SSHSchema._parseUser(all_elements["SSH_USER"])
        elif "SSH_USER" in fallbacks.keys():
            self._user = SSHSchema._parseUser(fallbacks["SSH_USER"])
        else:
            self._user = None
            Logger.Log(f"{name} config does not have a 'SSH_USER' element; defaulting to ssh_user={self._user}", logging.WARN)
        if "SSH_PW" in all_elements.keys():
            self._pass = SSHSchema._parsePass(all_elements["SSH_PW"])
        elif "SSH_PASS" in all_elements.keys():
            self._pass = SSHSchema._parsePass(all_elements["SSH_PASS"])
        elif "SSH_PW" in fallbacks.keys():
            self._pass = SSHSchema._parsePass(fallbacks["SSH_PW"])
        elif "SSH_PASS" in fallbacks.keys():
            self._pass = SSHSchema._parsePass(fallbacks["SSH_PASS"])
        else:
            self._pass = None
            Logger.Log(f"{name} config does not have a 'SSH_PASS' or 'SSH_PW' element; defaulting to ssh_pass={self._pass}", logging.WARN)
        if "SSH_PORT" in all_elements.keys():
            self._port = SSHSchema._parsePort(all_elements["SSH_PORT"])
        elif "SSH_PORT" in fallbacks.keys():
            self._port = SSHSchema._parsePort(fallbacks["SSH_PORT"])
        else:
            self._port = 22
            Logger.Log(f"{name} config does not have a 'SSH_PORT' element; defaulting to ssh_port={self._port}", logging.WARN)

        _used = {"SSH_HOST", "SSH_USER", "SSH_PW", "SSH_PASS", "SSH_PORT"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def Host(self) -> Optional[str]:
        return self._host

    @property
    def User(self) -> Optional[str]:
        return self._user

    @property
    def Pass(self) -> Optional[str]:
        return self._pass

    @property
    def Port(self) -> int:
        return self._port

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name} : `{self.AsConnectionInfo}`"
        return ret_val

    @property
    def AsConnectionInfo(self) -> str:
        ret_val : str

        ret_val = f"{self.User}@{self.Host}:{self.Port}"
        return ret_val

    @staticmethod
    def _parseHost(host) -> Optional[str]:
        ret_val : Optional[str]
        if isinstance(host, str):
            ret_val = host
        else:
            ret_val = str(host)
            Logger.Log(f"SSH config for host was unexpected type {type(host)}, defaulting to str(host)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseUser(user) -> Optional[str]:
        ret_val : Optional[str]
        if isinstance(user, str):
            ret_val = user
        else:
            ret_val = str(user)
            Logger.Log(f"SSH config for user was unexpected type {type(user)}, defaulting to str(user)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parsePass(pw) -> Optional[str]:
        ret_val : Optional[str]
        if isinstance(pw, str):
            ret_val = pw
        else:
            ret_val = str(pw)
            Logger.Log(f"SSH config for password was unexpected type {type(pw)}, defaulting to str(pw)=***.", logging.WARN)
        return ret_val

    @staticmethod
    def _parsePort(port) -> int:
        ret_val : int
        if isinstance(port, int):
            ret_val = port
        elif isinstance(port, str):
            ret_val = int(port)
        else:
            ret_val = int(port)
            Logger.Log(f"SSH config for port was unexpected type {type(port)}, defaulting to int(port)={ret_val}.", logging.WARN)
        return ret_val

class MySQLSchema(DataSourceSchema):
    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._db_host  : str
        self._db_port  : int
        self._db_user  : str
        self._db_pass  : Optional[str]
        self._ssh_cfg  : SSHSchema

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
        if "DB_USER" in all_elements.keys():
            self._db_user = MySQLSchema._parseDBUser(all_elements["DB_USER"])
        else:
            self._db_user = "UNKOWN"
            Logger.Log(f"{name} config does not have a 'DB_USER' element; defaulting to db_user={self._db_user}", logging.WARN)
        if "DB_PW" in all_elements.keys():
            self._db_pass = MySQLSchema._parseDBPass(all_elements["DB_PW"])
        elif "DB_PASS" in all_elements.keys():
            self._db_pass = MySQLSchema._parseDBPass(all_elements["DB_PASS"])
        else:
            self._db_pass = None
            Logger.Log(f"{name} config does not have a 'DB_PW' element; defaulting to db_pass=None", logging.WARN)
        # Parse SSH info, if it exists. Don't notify, if it doesn't exist.
        _ssh_keys = {"SSH_HOST", "SSH_PORT", "SSH_USER", "SSH_PW", "SSH_PASS"}
        self._ssh_cfg = SSHSchema(name=f"{name}-SSH", all_elements={ key : all_elements.get(key) for key in _ssh_keys.intersection(all_elements.keys()) })

        _used = {"DB_HOST", "DB_PORT", "DB_USER", "DB_PW", "DB_PASS", "SSH_HOST", "SSH_PORT", "SSH_USER", "SSH_PW", "SSH_PASS"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def DBHost(self) -> str:
        return self._db_host

    @property
    def DBPort(self) -> int:
        return self._db_port

    @property
    def DBUser(self) -> str:
        return self._db_user

    @property
    def DBPass(self) -> Optional[str]:
        return self._db_pass

    @property
    def SSHConfig(self) -> SSHSchema:
        return self._ssh_cfg

    @property
    def SSH(self) -> SSHSchema:
        """Shortened alias for SSHConfig, convenient when using sub-elements of the SSHConfig.

        :return: The schema describing the configuration for an SSH connection to a data source.
        :rtype: SSHSchema
        """
        return self._ssh_cfg

    @property
    def HasSSH(self) -> bool:
        """Property indicating if this MySQL source has a valid SSH configuration attached to it.

        :return: True if there is a valid SSH configuration, otherwise false.
        :rtype: bool
        """
        return (self.SSH.Host is not None and self.SSH.User is not None and self.SSH.Pass is not None)

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ssh_part = f"{self.SSH.AsConnectionInfo} -> " if self.HasSSH else ""
        ret_val  = f"{self.Name} : `{ssh_part}{self.AsConnectionInfo}` ({self.Type})"
        return ret_val

    @property
    def AsConnectionInfo(self) -> str:
        ret_val : str = f"{self.DBUser}@{self.DBHost}:{self.DBPort}"
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

