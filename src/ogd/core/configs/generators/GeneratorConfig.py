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
        """Constructor for the `GeneratorConfig` class.
        
        If optional params are not given, data is searched for in `other_elements`.
        Because `GeneratorConfig` is just a base class for other specific generator configuration classes,
        the sample format below includes keys not used by `GeneratorConfig`.
        The actual keys used are `enabled`, `type`, and `description`.
        `subfeatures` is an optional key.

        Expected format:

        ```
        {
            "enabled": true,
            "type": "ExtractorType",
            "description": "Human-readable description of the feature this module extracts.",
            "return_type": "str"
        }
        ```

        :param name: _description_
        :type name: str
        :param enabled: _description_
        :type enabled: Optional[Set[ExtractionMode]]
        :param type_name: _description_
        :type type_name: Optional[str]
        :param description: _description_
        :type description: Optional[str]
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._enabled     : Set[ExtractionMode]
        self._type_name   : str
        self._description : str

        self._enabled     = enabled     if enabled     is not None else self._parseEnabled(unparsed_elements=unparsed_elements, schema_name=name)
        self._type_name   = type_name   if type_name   is not None else self._parseType(unparsed_elements=unparsed_elements, schema_name=name)
        self._description = description if description is not None else self._parseDescription(unparsed_elements=unparsed_elements, schema_name=name)

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
    def _parseType(unparsed_elements:Map, schema_name:Optional[str]=None) -> str:
        return GeneratorConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["type"],
            to_type=str,
            default_value=GeneratorConfig._DEFAULT_TYPE,
            remove_target=True,
            schema_name=schema_name
        )

    @staticmethod
    def _parseEnabled(unparsed_elements:Map, schema_name:Optional[str]=None) -> Set[ExtractionMode]:
        ret_val : Set[ExtractionMode] = set()

        enabled = GeneratorConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=['enabled'],
            to_type=[bool, list],
            default_value=GeneratorConfig._DEFAULT_ENABLED,
            remove_target=True,
            schema_name=schema_name
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
    def _parseDescription(unparsed_elements:Map, schema_name:Optional[str]=None) -> str:
        return GeneratorConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=['description'],
            to_type=str,
            default_value=GeneratorConfig._DEFAULT_DESCRIPTION,
            remove_target=True,
            schema_name=schema_name
        )
