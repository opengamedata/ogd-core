# import standard libraries
import logging
from pathlib import Path
from typing import Any, Dict, Optional
# import local files
from ogd.core.schemas.Schema import Schema
from ogd.core.utils.Logger import Logger

class FileIndexingSchema(Schema):
    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._local_dir     : Path
        self._remote_url    : Optional[str]
        self._templates_url : str

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} base config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        if "LOCAL_DIR" in all_elements.keys():
            self._local_dir = FileIndexingSchema._parseLocalDir(all_elements["LOCAL_DIR"])
        else:
            self._local_dir = Path("./data/")
            Logger.Log(f"{name} config does not have a 'LOCAL_DIR' element; defaulting to local_dir={self._local_dir}", logging.WARN)
        if "REMOTE_URL" in all_elements.keys():
            self._remote_url = FileIndexingSchema._parseRemoteURL(all_elements["REMOTE_URL"])
        else:
            self._remote_url = None
            Logger.Log(f"{name} config does not have a 'REMOTE_URL' element; defaulting to remote_url={self._remote_url}", logging.WARN)
        if "TEMPLATES_URL" in all_elements.keys():
            self._templates_url = FileIndexingSchema._parseTemplatesURL(all_elements["TEMPLATES_URL"])
        else:
            self._templates_url = "https://github.com/opengamedata/opengamedata-samples"
            Logger.Log(f"{name} config does not have a 'TEMPLATES_URL' element; defaulting to templates_url={self._templates_url}", logging.WARN)

        _used = {"LOCAL_DIR", "REMOTE_URL", "TEMPLATES_URL"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def LocalDirectory(self) -> Path:
        return self._local_dir

    @property
    def RemoteURL(self) -> Optional[str]:
        return self._remote_url

    @property
    def TemplatesURL(self) -> str:
        return self._templates_url

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name} : Local=_{self.LocalDirectory}_, Remote=_{self.RemoteURL}_"
        return ret_val

    @staticmethod
    def _parseLocalDir(dir) -> Path:
        ret_val : Path
        if isinstance(dir, Path):
            ret_val = dir
        elif isinstance(dir, str):
            ret_val = Path(dir)
        else:
            ret_val = Path(str(dir))
            Logger.Log(f"File Indexing local data directory was unexpected type {type(dir)}, defaulting to Path(str(dir))={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseRemoteURL(url) -> str:
        ret_val : str
        if isinstance(url, str):
            ret_val = url
        else:
            ret_val = str(url)
            Logger.Log(f"File indexing remote url was unexpected type {type(url)}, defaulting to str(url)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseTemplatesURL(url) -> str:
        ret_val : str
        if isinstance(url, str):
            ret_val = url
        else:
            ret_val = str(url)
            Logger.Log(f"File indexing remote url was unexpected type {type(url)}, defaulting to str(url)={ret_val}.", logging.WARN)
        return ret_val
