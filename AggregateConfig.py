"""Aggregate Feature Config Module
"""
# import standard libraries
from typing import Any, Dict, Optional, Set
# import local files
from ogd.common.configs.games.FeatureConfig import FeatureConfig, SubfeatureConfig
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.utils.typing import Map

class AggregateConfig(FeatureConfig):
    """Schema for tracking the configuration of an aggregate feature.
    """
    def __init__(self, name:str,
                 # params for class
                 # params for parent
                 return_type:Optional[str]=None, subfeatures:Optional[Dict[str, SubfeatureConfig]]=None,
                 enabled:Optional[Set[ExtractionMode]]=None, type_name:Optional[str]=None, description:Optional[str]=None,
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
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
    def FromDict(cls, name:str, unparsed_elements:Dict[str, Any])-> "AggregateConfig":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: AggregateConfig
        """
        return AggregateConfig(name=name, other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "AggregateConfig":
        return AggregateConfig(
            name="DefaultAggregateConfig",
            other_elements={}
        )
