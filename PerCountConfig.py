# import standard libraries
from typing import Dict, Optional, Set
# import local files
from ogd.common.configs.generators.FeatureConfig import FeatureConfig
from ogd.common.configs.generators.SubfeatureConfig import SubfeatureConfig
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.utils.typing import Map

class PerCountConfig(FeatureConfig):

    _DEFAULT_COUNT = 1
    _DEFAULT_PREFIX = "pre"

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str,
                 # params for class
                 count:Optional[int|str], prefix:Optional[str],
                 # params for parent
                 return_type:Optional[str]=None, subfeatures:Optional[Dict[str, SubfeatureConfig]]=None,
                 enabled:Optional[Set[ExtractionMode]]=None, type_name:Optional[str]=None, description:Optional[str]=None,
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        """Constructor for the `PerCountConfig` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "enabled": true,
            "type": "ExtractorClass",
            "count": "level_range",
            "prefix": "lvl",
            "description": "Info about the per-count extractor; the per-count is generally optional.",
            "return_type": "str"
        },
        ```

        :param name: _description_
        :type name: str
        :param count: _description_
        :type count: Optional[int | str]
        :param prefix: _description_
        :type prefix: Optional[str]
        :param return_type: _description_, defaults to None
        :type return_type: Optional[str], optional
        :param subfeatures: _description_, defaults to None
        :type subfeatures: Optional[Dict[str, SubfeatureConfig]], optional
        :param enabled: _description_, defaults to None
        :type enabled: Optional[Set[ExtractionMode]], optional
        :param type_name: _description_, defaults to None
        :type type_name: Optional[str], optional
        :param description: _description_, defaults to None
        :type description: Optional[str], optional
        :param other_elements: _description_, defaults to None
        :type other_elements: Optional[Map], optional
        """
        unparsed_elements : Map = other_elements or {}

        self._count  : int | str = count  or self._parseCount(unparsed_elements=unparsed_elements)
        self._prefix : str       = prefix or self._parsePrefix(unparsed_elements=unparsed_elements)

        super().__init__(name=name, return_type=return_type, subfeatures=subfeatures, enabled=enabled, type_name=type_name, description=description, other_elements=unparsed_elements)

    @property
    def Count(self) -> int | str:
        """Property for the 'count' of instances for the Per-Count Feature

        :return: _description_
        :rtype: int | str
        """
        return self._count

    @property
    def Prefix(self) -> str:
        return self._prefix

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val   : str

        ret_val = f"**{self.Name}** : *{self.ReturnType}*, *Per-count feature* {' (disabled)' if not len(self.Enabled) > 0 else ''}  \n{self.Description}  \n"
        if len(self.Subfeatures) > 0:
            ret_val += "*Sub-features*:  \n\n" + "\n".join([subfeature.AsMarkdown for subfeature in self.Subfeatures.values()])
        if len(self.NonStandardElements) > 0:
            ret_val += "*Other elements*:  \n\n" + "\n".join([f"{elem_name} : {elem}" for elem_name,elem in self.NonStandardElements.items()])
        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None)-> "PerCountConfig":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: PerCountConfig
        """
        return PerCountConfig(name=name, count=None, prefix=None, other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "PerCountConfig":
        return PerCountConfig(
            name="DefaultPerCountConfig",
            count=cls._DEFAULT_COUNT,
            prefix=cls._DEFAULT_PREFIX,
            other_elements={}
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseCount(unparsed_elements:Map) -> int | str:
        return PerCountConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["count"],
            to_type=[int, str],
            default_value=PerCountConfig._DEFAULT_COUNT,
            remove_target=True
        )

    @staticmethod
    def _parsePrefix(unparsed_elements:Map) -> str:
        return PerCountConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["prefix"],
            to_type=str,
            default_value=PerCountConfig._DEFAULT_PREFIX,
            remove_target=True
        )

    # *** PRIVATE METHODS ***
