# import standard libraries
import logging
from typing import Any, Dict, Union
# import local files
from schemas.game_schemas.FeatureSchema import FeatureSchema
from utils import Logger

class PerCountSchema(FeatureSchema):
    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._count  : Union[int, str]
        self._prefix : str


        if isinstance(all_elements, dict):
            if "count" in all_elements.keys():
                self._count = PerCountSchema._parseCount(all_elements["count"])
            else:
                self._count = 0
                Logger.Log(f"{name} config does not have an 'count' element; defaulting to count=0", logging.WARN)
            if "prefix" in all_elements.keys():
                self._prefix = PerCountSchema._parsePrefix(all_elements['prefix'])
            else:
                self._prefix = "pre"
                Logger.Log(f"{name} config does not have an 'prefix' element; defaulting to prefix='pre'", logging.WARN)
        else:
            all_elements = {}
            Logger.Log(f"For {name} Per-count Feature config, all_elements was not a dict, defaulting to empty dict", logging.WARN)

        self._elements = { key : val for key,val in all_elements.items() if key not in ["count", "prefix"] }
        super().__init__(name=name, all_elements=all_elements)

    @property
    def Count(self) -> Union[int, str]:
        return self._name

    @property
    def Prefix(self) -> str:
        return self._prefix

    @property
    def AsMarkdown(self) -> str:
        ret_val   : str

        ret_val = f"**{self.Name}** : *{self.ReturnType}*, *Per-count feature* {' (disabled)' if not len(self.Enabled) > 0 else ''}  \n{self.Description}  \n"
        if len(self.Subfeatures) > 0:
            ret_val += "*Sub-features*:  \n\n" + "\n".join([subfeature.AsMarkdown for subfeature in self.Subfeatures.values()])
        if len(self.Elements) > 0:
            ret_val += "*Other elements*:  \n\n" + "\n".join([f"{elem_name} - {elem}" for elem_name,elem in self.Elements.items()])
        return ret_val

    @staticmethod
    def _parseCount(count) -> Union[int, str]:
        ret_val : Union[int, str]
        if isinstance(count, int):
            ret_val = count
        elif isinstance(count, str):
            ret_val = count
        else:
            ret_val = 0
            Logger.Log(f"Extractor count was unexpected type {type(count)}, defaulting to count=0.", logging.WARN)
        return ret_val

    @staticmethod
    def _parsePrefix(prefix) -> str:
        ret_val : str
        if isinstance(prefix, str):
            ret_val = prefix
        else:
            ret_val = str(prefix)
            Logger.Log(f"Extractor prefix was unexpected type {type(prefix)}, defaulting to str(prefix).", logging.WARN)
        return ret_val
