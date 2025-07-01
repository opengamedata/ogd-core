# import standard libraries
import logging
from typing import Any, Dict, Optional, Set
# import local files
from ogd.common.configs.Config import Config
from ogd.common.configs.generators.GeneratorConfig import GeneratorConfig
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

class SubfeatureConfig(Config):
    _DEFAULT_RETURN_TYPE = "str"
    _DEFAULT_DESCRIPTION = "Default Subfeature schema object. Does not correspond to any actual data."

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 # params for class
                 return_type:Optional[str], description:Optional[str],
                 # params for parent
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        unparsed_elements : Map = other_elements or {}
        
        self._return_type : str = return_type or self._parseReturnType(unparsed_elements=unparsed_elements)
        self._description : str = description or self._parseDescription(unparsed_elements=unparsed_elements)

        super().__init__(name=name, other_elements=other_elements)

    @property
    def ReturnType(self) -> str:
        return self._return_type

    @property
    def Description(self) -> str:
        return self._description

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = f"- **{self.Name}** : *{self.ReturnType}*, {self.Description}  \n"
        if len(self.NonStandardElements) > 0:
            ret_val += f'   (other items: {self.NonStandardElements}'
        return ret_val

    @classmethod
    def FromDict(cls, name:str, unparsed_elements:Dict[str, Any])-> "SubfeatureConfig":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: SubfeatureConfig
        """
        _return_type : str
        _description : str    

        if not isinstance(unparsed_elements, dict):
            _elements = {}
            Logger.Log(f"For {name} subfeature config, unparsed_elements was not a dict, defaulting to empty dict", logging.WARN)

        _return_type = cls._parseReturnType(unparsed_elements=unparsed_elements)
        _description = cls._parseDescription(unparsed_elements=unparsed_elements)

        _used = {"return_type", "description"}
        _leftovers = { key : val for key,val in unparsed_elements.items() if key not in _used }
        return SubfeatureConfig(name=name, return_type=_return_type, description=_description, other_elements=_leftovers)

    @classmethod
    def Default(cls) -> "SubfeatureConfig":
        return SubfeatureConfig(
            name="DefaultSubFeatureConfig",
            return_type=cls._DEFAULT_RETURN_TYPE,
            description=cls._DEFAULT_DESCRIPTION,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseReturnType(unparsed_elements:Map) -> str:
        return SubfeatureConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["return_type"],
            to_type=str,
            default_value=SubfeatureConfig._DEFAULT_RETURN_TYPE,
            remove_target=True
        )

    @staticmethod
    def _parseDescription(unparsed_elements:Map):
        return SubfeatureConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["description"],
            to_type=str,
            default_value=SubfeatureConfig._DEFAULT_DESCRIPTION,
            remove_target=True
        )

    # *** PRIVATE METHODS ***

class FeatureConfig(GeneratorConfig):
    """Base class for all schemas related to defining feature Extractor configurations.
    """
    _DEFAULT_RETURN_TYPE = "str"
    _DEFAULT_SUBFEATURES = {}

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 # params for class
                 return_type:Optional[str], subfeatures:Optional[Dict[str, SubfeatureConfig]],
                 # params for parent
                 enabled:Optional[Set[ExtractionMode]]=None, type_name:Optional[str]=None, description:Optional[str]=None,
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        unparsed_elements : Map = other_elements or {}

        self._subfeatures : Dict[str, SubfeatureConfig] = subfeatures or FeatureConfig._parseSubfeatures(unparsed_elements=unparsed_elements)
        self._return_type : str                         = return_type or FeatureConfig._parseReturnType(unparsed_elements=unparsed_elements)

        # Don't explicitly pass in other params, let them be parsed from other_elements.
        super().__init__(name=name, enabled=enabled, type_name=type_name, description=description, other_elements=unparsed_elements)

    @property
    def ReturnType(self) -> str:
        return self._return_type

    @property
    def Subfeatures(self) -> Dict[str, SubfeatureConfig]:
        return self._subfeatures

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseReturnType(unparsed_elements:Map) -> str:
        return FeatureConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["return_type"],
            to_type=str,
            default_value=FeatureConfig._DEFAULT_RETURN_TYPE,
            remove_target=True
        )

    @staticmethod
    def _parseSubfeatures(unparsed_elements) -> Dict[str, SubfeatureConfig]:
        ret_val : Dict[str, SubfeatureConfig]

        subfeatures = FeatureConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["subfeatures"],
            to_type=dict,
            default_value=FeatureConfig._DEFAULT_SUBFEATURES,
            remove_target=True
        )
        if isinstance(subfeatures, dict):
            ret_val = {name:SubfeatureConfig.FromDict(name=name, unparsed_elements=elems) for name,elems in subfeatures.items()}
        else:
            ret_val = {}
            Logger.Log(f"Extractor subfeatures was unexpected type {type(subfeatures)}, defaulting to empty list.", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
