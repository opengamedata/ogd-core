# import standard libraries
import abc
import logging
from typing import Any, Dict, List, Set
# import local files
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.schemas.Schema import Schema
from ogd.core.utils.Logger import Logger

class ExtractorSchema(Schema):
    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._enabled     : Set[ExtractionMode]
        self._type_name   : str
        self._description : str

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} Extractor config, all_elements was not a dict, defaulting to empty dict", logging.WARN)

        if "type" in all_elements.keys():
            self._type_name = ExtractorSchema._parseType(all_elements['type'])
        else:
            self._type_name = name
        if "enabled" in all_elements.keys():
            self._enabled = ExtractorSchema._parseEnabled(all_elements['enabled'])
        else:
            self._enabled = {ExtractionMode.DETECTOR, ExtractionMode.SESSION, ExtractionMode.PLAYER, ExtractionMode.POPULATION}
            Logger.Log(f"{name} config does not have an 'enabled' element; defaulting to enabled=True", logging.WARN)
        if "description" in all_elements.keys():
            self._description = ExtractorSchema._parseDescription(all_elements['description'])
        else:
            self._description = "No Description"
            Logger.Log(f"{name} config does not have an 'description' element; defaulting to description='{self._description}'", logging.WARN)

        _leftovers = { key : val for key,val in all_elements.items() if key not in {"type", "enabled", "description"} }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def TypeName(self) -> str:
        return self._type_name

    @property
    def Enabled(self) -> Set[ExtractionMode]:
        return self._enabled

    @property
    def Description(self) -> str:
        return self._description
    
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
                mode = str(mode).upper()
                match mode:
                    case "DETECTOR":
                        ret_val.add(ExtractionMode.DETECTOR)
                    case "SESSION":
                        ret_val.add(ExtractionMode.SESSION)
                    case "PLAYER":
                        ret_val.add(ExtractionMode.PLAYER)
                    case "POPULATION":
                        ret_val.add(ExtractionMode.POPULATION)
                    case _:
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
