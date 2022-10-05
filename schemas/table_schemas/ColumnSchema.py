# import standard libraries
import logging
from typing import Any, Dict, List, Set
# import local files
from schemas.ExtractionMode import ExtractionMode
from utils import Logger

class ColumnSchema:
    def __init__(self, all_elements:Dict[str, Any]):
        self._name        : str
        self._readable    : str
        self._value_type  : str
        self._description : str
        self._elements    : Dict[str, Any]

        if isinstance(all_elements, dict):
            if "name" in all_elements.keys():
                self._name = ColumnSchema._parseName(all_elements['name'])
            else:
                self._name = "NOT FOUND"
                Logger.Log(f"Column config does not have a 'name' element; defaulting to name=NOT FOUND", logging.WARN)

            if "readable" in all_elements.keys():
                self._readable = ColumnSchema._parseReadable(all_elements['readable'])
            else:
                self._readable = self._name
                Logger.Log(f"{self._name} config does not have a 'readable' element; defaulting to readable=name", logging.WARN)

            if "description" in all_elements.keys():
                self._description = ColumnSchema._parseDescription(all_elements['description'])
            else:
                self._description = ""
                Logger.Log(f"{self._name} config does not have an 'description' element; defaulting to description=''", logging.WARN)

            if "type" in all_elements.keys():
                self._value_type = ColumnSchema._parseValueType(all_elements['type'])
            else:
                self._value_type = self._name
            self._elements = { key : val for key,val in all_elements.items() if key not in {"name", "readable", "description", "type"} }
        else:
            self._name        = "No Name"
            self._readable    = "No Readable Name"
            self._description = "No Description"
            self._value_type  = "No Type"
            self._elements = {}
            Logger.Log(f"For {self._name} Extractor config, all_elements was not a dict, defaulting to empty dict", logging.WARN)

    def __str__(self):
        return self.Name

    def __repr__(self):
        return self.Name

    @property
    def Name(self) -> str:
        return self._name

    @property
    def ReadableName(self) -> str:
        return self._name

    @property
    def Description(self) -> str:
        return self._description

    @property
    def ValueType(self) -> str:
        return self._value_type

    @property
    def Elements(self) -> Dict[str, Any]:
        return self._elements

    @property
    def ElementNames(self) -> List[str]:
        return list(self._elements.keys())

    @property
    def AsMarkdown(self) -> str:
        ret_val = f"**{self.Name}** : *{self.ValueType}* - {self.ReadableName}, {self.Description}  "

        if len(self.Elements) > 0:
            other_elems = [f"{key}: {val}" for key,val in self.Elements]
            ret_val += f"\n    Other Elements: {', '.join(other_elems)}"

        return ret_val
    
    @staticmethod
    def _parseName(name):
        ret_val : str
        if isinstance(name, str):
            ret_val = name
        else:
            ret_val = str(name)
            Logger.Log(f"Column name was not a string, defaulting to str(name) == {ret_val}", logging.WARN)
        return ret_val
    
    @staticmethod
    def _parseReadable(name):
        ret_val : str
        if isinstance(name, str):
            ret_val = name
        else:
            ret_val = str(name)
            Logger.Log(f"Column readable name was not a string, defaulting to str(readable) == {ret_val}", logging.WARN)
        return ret_val
    
    @staticmethod
    def _parseDescription(description):
        ret_val : str
        if isinstance(description, str):
            ret_val = description
        else:
            ret_val = str(description)
            Logger.Log(f"Column description was not a string, defaulting to str(description) == {ret_val}", logging.WARN)
        return ret_val
    
    @staticmethod
    def _parseValueType(extractor_type):
        ret_val : str
        if isinstance(extractor_type, str):
            ret_val = extractor_type
        else:
            ret_val = str(extractor_type)
            Logger.Log(f"Column type was not a string, defaulting to str(type) == {ret_val}", logging.WARN)
        return ret_val
