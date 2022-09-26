# import standard libraries
import abc
import logging
from typing import Any, Dict, List, Set
# import local files
from schemas.ExtractionMode import ExtractionMode
from utils import Logger

class ExtractorSchema(abc.ABC):
    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._name        : str = name
        self._enabled     : Set[ExtractionMode]
        self._type_name   : str
        self._description : str
        self._elements    : Dict[str, Any]

        self._name = ExtractorSchema._parseName(name)
        if isinstance(all_elements, dict):
            if "type" in all_elements.keys():
                self._type_name = ExtractorSchema._parseType(all_elements['type'])
            else:
                self._type_name = self._name

            if "enabled" in all_elements.keys():
                self._enabled = ExtractorSchema._parseEnabled(all_elements['enabled'])
            else:
                self._enabled = {ExtractionMode.DETECTOR, ExtractionMode.SESSION, ExtractionMode.PLAYER, ExtractionMode.POPULATION}
                Logger.Log(f"{name} config does not have an 'enabled' element; defaulting to enabled=True", logging.WARN)

            if "description" in all_elements.keys():
                self._description = ExtractorSchema._parseDescription(all_elements['description'])
            else:
                self._description = ""
                Logger.Log(f"{name} config does not have an 'description' element; defaulting to description=''", logging.WARN)
            self._elements = { key : val for key,val in all_elements.items() if key not in {"type", "enabled", "description"} }
        else:
            self._enabled = set()
            self._description = "No Description"
            self._elements = {}
            Logger.Log(f"For {name} Extractor config, all_elements was not a dict, defaulting to empty dict", logging.WARN)

    @property
    def Name(self) -> str:
        return self._name

    @property
    def TypeName(self) -> str:
        return self._type_name

    @property
    def Enabled(self) -> Set[ExtractionMode]:
        return self._enabled

    @property
    def Description(self) -> str:
        return self._description

    @property
    def Elements(self) -> Dict[str, Any]:
        return self._elements

    @property
    def ElementNames(self) -> List[str]:
        return list(self._elements.keys())

    @property
    @abc.abstractmethod
    def AsMarkdown(self) -> str:
        pass
    
    @staticmethod
    def _parseName(name):
        ret_val : str
        if isinstance(name, str):
            ret_val = name
        else:
            ret_val = str(name)
            Logger.Log(f"Extractor name was not a string, defaulting to str(name) == {ret_val}", logging.WARN)
        return ret_val
    
    @staticmethod
    def _parseType(extractor_type):
        ret_val : str
        if isinstance(extractor_type, str):
            ret_val = extractor_type
        else:
            ret_val = str(extractor_type)
            Logger.Log(f"Extractor type was not a string, defaulting to str(type) == {ret_val}", logging.WARN)
        return ret_val

    @staticmethod
    def _parseEnabled(enabled):
        ret_val : Set[ExtractionMode] = set()
        if isinstance(enabled, bool):
            if enabled:
                ret_val = {ExtractionMode.DETECTOR, ExtractionMode.SESSION, ExtractionMode.PLAYER, ExtractionMode.POPULATION}
            else:
                ret_val = set()
        elif isinstance(enabled, list):
            for mode in enabled:
                mode = str(mode)
                if mode.upper() == "DETECTOR":
                    ret_val.add(ExtractionMode.DETECTOR)
                elif mode.upper() == "SESSION":
                    ret_val.add(ExtractionMode.SESSION)
                elif mode.upper() == "PLAYER":
                    ret_val.add(ExtractionMode.PLAYER)
                elif mode.upper() == "POPULATION":
                    ret_val.add(ExtractionMode.POPULATION)
                else:
                    Logger.Log(f"Found unrecognized element of 'enabled': {mode}", logging.WARN)
        else:
            ret_val = {ExtractionMode.DETECTOR, ExtractionMode.SESSION, ExtractionMode.PLAYER, ExtractionMode.POPULATION}
            Logger.Log(f"'enabled' element has unrecognized type {type(enabled)}; defaulting to enable all modes", logging.WARN)
        return ret_val
    
    @staticmethod
    def _parseDescription(description):
        ret_val : str
        if isinstance(description, str):
            ret_val = description
        else:
            ret_val = str(description)
            Logger.Log(f"Extractor description was not a string, defaulting to str(description) == {ret_val}", logging.WARN)
        return ret_val
