"""Aggregate Feature Config Module
"""
# import standard libraries
from typing import Dict, Optional, Set
# import local files
from ogd.common.configs.generators.FeatureConfig import FeatureConfig
from ogd.common.configs.generators.SubfeatureConfig import SubfeatureConfig
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.utils.typing import Map

class AggregateConfig(FeatureConfig):
    """Schema for tracking the configuration of an aggregate feature."""

    def __init__(self, name:str,
                 # params for class
                 # params for parent
                 return_type:Optional[str]=None, subfeatures:Optional[Dict[str, SubfeatureConfig]]=None,
                 enabled:Optional[Set[ExtractionMode]]=None, type_name:Optional[str]=None, description:Optional[str]=None,
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        """Constructor for the `AggregateConfig` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "enabled": true,
            "type": "FeatureClass",
            "description": "Human-readable description of the feature value",
            "return_type": "str"
        },
        ```

        :param name: _description_
        :type name: str
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
        super().__init__(name=name, return_type=return_type, subfeatures=subfeatures, enabled=enabled, type_name=type_name, description=description, other_elements=unparsed_elements)

    @property
    def AsMarkdown(self) -> str:
        ret_val   : str

        ret_val = f"**{self.Name}** : *{self.ReturnType}*, *Aggregate feature* {' (disabled)' if not len(self.Enabled) > 0 else ''}  \n{self.Description}  \n"
        if len(self.Subfeatures) > 0:
            ret_val += "*Sub-features*:  \n\n" + "\n".join([subfeature.AsMarkdown for subfeature in self.Subfeatures.values()])
        if len(self.NonStandardElements) > 0:
            ret_val += "*Other elements*:  \n\n" + "\n".join([f"{elem_name} : {elem}" for elem_name,elem in self.NonStandardElements.items()])
        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map, key_overrides:Optional[Dict[str, str]]=None)-> "AggregateConfig":
        """Function to parse an AggregateConfig from a dictionary.

        Expected format:

        ```
        {
            "enabled": true,
            "type": "FeatureClass",
            "description": "Human-readable description of the feature value",
            "return_type": "str"
        },
        ```

        :param name: The name associated with the feature, typically but not always equal to the `"type"` value.
        :type name: str
        :param unparsed_elements: The dictionary containing the contents for the `AggregateConfig`
        :type unparsed_elements: Map
        :param key_overrides: (_Ignored_) A dictionary of overrides for keys to look for, defaults to None
        :type key_overrides: Optional[Dict[str, str]], optional
        :return: An `AggregateConfig` with data from the given `unparsed_elements`
        :rtype: AggregateConfig
        """
        return AggregateConfig(name=name, other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "AggregateConfig":
        return AggregateConfig(
            name="DefaultAggregateConfig",
            other_elements={}
        )
