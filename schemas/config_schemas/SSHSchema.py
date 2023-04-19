# import standard libraries
import logging
from pathlib import Path
from typing import Any, Dict, Optional
# import local files
from schemas.Schema import Schema
from utils import Logger

class SSHSchema(Schema):
    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._host : Optional[str]
        self._user : Optional[str]
        self._pass : Optional[str]
        self._port : int

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} base config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        if "SSH_HOST" in all_elements.keys():
            self._ssh_host = SSHSchema._parseHost(all_elements["SSH_HOST"])
        else:
            self._ssh_host = None
            Logger.Log(f"{name} config does not have a 'SSH_HOST' element; defaulting to ssh_host={self._ssh_host}", logging.WARN)
        if "SSH_USER" in all_elements.keys():
            self._user = SSHSchema._parseUser(all_elements["SSH_USER"])
        else:
            self._user = None
            Logger.Log(f"{name} config does not have a 'SSH_USER' element; defaulting to ssh_user={self._user}", logging.WARN)
        if "SSH_PW" in all_elements.keys():
            self._pass = SSHSchema._parsePass(all_elements["SSH_PW"])
        elif "SSH_PASS" in all_elements.keys():
            self._pass = SSHSchema._parsePass(all_elements["SSH_PASS"])
        else:
            self._pass = None
            Logger.Log(f"{name} config does not have a 'SSH_PASS' or 'SSH_PW' element; defaulting to ssh_pass={self._pass}", logging.WARN)
        if "SSH_PORT" in all_elements.keys():
            self._port = SSHSchema._parsePort(all_elements["SSH_PORT"])
        else:
            self._port = 22
            Logger.Log(f"{name} config does not have a 'SSH_PORT' element; defaulting to ssh_port={self._port}", logging.WARN)

        _leftovers = { key : val for key,val in all_elements.items() if key not in {"LOCAL_DIR", "REMOTE_URL", "TEMPLATES_URL"} }
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

        ret_val = f"{self.Name} : `{self.User}@{self.Host}:{self.Port}`"
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
            Logger.Log(f"SSH config for port was unexpected type {type(port)}, defaulting to str(port)={ret_val}.", logging.WARN)
        return ret_val
