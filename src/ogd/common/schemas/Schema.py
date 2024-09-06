# import standard libraries
import abc
import logging
from typing import Any, Dict, List, Optional
# import local files
from ogd.core.utils.Logger import Logger

class Schema(abc.ABC):
    def __init__(self, name:str, other_elements:Optional[Dict[str, Any]]):
        self._name : str
        self._other_elements : Dict[str, Any]

        self._name = Schema._parseName(name)

        self._other_elements = other_elements or {}
        if len(self._other_elements.keys()) > 0:
            Logger.Log(f"Schema for {self.Name} contained nonstandard elements {self.NonStandardElementNames}")

    def __str__(self):
        return f"{type(self).__name__}[{self.Name}]"

    def __repr__(self):
        return f"{type(self).__name__}[{self.Name}]"

    @property
    @abc.abstractmethod
    def AsMarkdown(self) -> str:
        pass

    @property
    def Name(self) -> str:
        return self._name

    @property
    def NonStandardElements(self) -> Dict[str, Any]:
        return self._other_elements

    @property
    def NonStandardElementNames(self) -> List[str]:
        return list(self._other_elements.keys())
    
    @staticmethod
    def _parseName(name):
        ret_val : str
        if isinstance(name, str):
            ret_val = name
        else:
            ret_val = str(name)
            Logger.Log(f"Schema name was not a string, defaulting to str(name) == {ret_val}", logging.WARN)
        return ret_val