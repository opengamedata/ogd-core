# import standard libraries
import logging
from typing import Optional, Set
# import local files
from ogd.common.configs.Config import Config
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class GeneratorConfig(Config):

    _DEFAULT_TYPE = "UNKNOWN TYPE"
    _DEFAULT_ENABLED = True
    _DEFAULT_DESCRIPTION = "Default Generator schema object. Does not correspond to any actual data."

    def __init__(self, name:str, enabled:Optional[Set[ExtractionMode]], type_name:Optional[str], description:Optional[str], other_elements:Optional[Map]=None):
        unparsed_elements : Map = other_elements or {}

        self._enabled     : Set[ExtractionMode]
        self._type_name   : str
        self._description : str

        self._enabled     = enabled     or GeneratorConfig._parseEnabled(unparsed_elements=unparsed_elements)
        self._type_name   = type_name   or GeneratorConfig._parseType(unparsed_elements=unparsed_elements)
        self._description = description or GeneratorConfig._parseDescription(unparsed_elements=unparsed_elements)

        super().__init__(name=name, other_elements=unparsed_elements)

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
    def _parseType(unparsed_elements:Map):
        return GeneratorConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["type"],
            to_type=str,
            default_value=GeneratorConfig._DEFAULT_TYPE,
            remove_target=True
        )

    @staticmethod
    def _parseEnabled(unparsed_elements:Map) -> Set[ExtractionMode]:
        ret_val : Set[ExtractionMode] = set()

        enabled = GeneratorConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=['enabled'],
            to_type=[bool, list],
            default_value=GeneratorConfig._DEFAULT_ENABLED,
            remove_target=True
        )
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
    def _parseDescription(unparsed_elements:Map) -> str:
        return GeneratorConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=['description'],
            to_type=str,
            default_value=GeneratorConfig._DEFAULT_DESCRIPTION,
            remove_target=True
        )
