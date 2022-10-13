# import standard libraries
import logging
from typing import Dict, List
# import local files
from utils import Logger

class EventSchema:
    def __init__(self, name:str, all_elements:Dict[str, str]):
        self._name     : str
        self._elements : Dict[str, str]

        if type(name) == str:
            self._name = name
        else:
            self._name = str(name)
            Logger.Log(f"Event name was not a string, defaulting to str(name) == {self._name}", logging.WARN)
        if type(all_elements) == dict:
            self._elements = all_elements
        else:
            self._elements = {}
            Logger.Log(f"For {name} Event config, all_elements was not a dict, defaulting to empty dict", logging.WARN)

    @property
    def Name(self) -> str:
        return self._name

    @property
    def Elements(self) -> Dict[str, str]:
        return self._elements

    @property
    def ElementNames(self) -> List[str]:
        return list(self._elements.keys())

    @property
    def AsMarkdown(self) -> str:
        return "\n".join([f"**{self.Name}**:  "] + [f"- **{elem_name}**: {elem_desc}  " for elem_name,elem_desc in self.Elements])
