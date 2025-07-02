# import standard libraries
import logging
from typing import Dict, Optional, Set
# import local files
from ogd.common.configs.generators.GeneratorConfig import GeneratorConfig
from ogd.common.configs.generators.SubfeatureConfig import SubfeatureConfig
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map

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
        unparsed_elements : Map = {key.upper() : val for key, val in other_elements.items()} if other_elements else {}

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
            ret_val = {name:SubfeatureConfig._fromDict(name=name, unparsed_elements=elems) for name,elems in subfeatures.items()}
        else:
            ret_val = {}
            Logger.Log(f"Extractor subfeatures was unexpected type {type(subfeatures)}, defaulting to empty list.", logging.WARN)
        return ret_val

    # *** PRIVATE METHODS ***
