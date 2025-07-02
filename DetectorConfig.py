"""Detector Config Module
"""
# import standard libraries
from typing import Any, Dict, Optional, Set
# import local files
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.configs.generators.GeneratorConfig import GeneratorConfig
from ogd.common.utils.typing import Map

class DetectorConfig(GeneratorConfig):
    """Schema for tracking the configuration of a detector.
    """
    def __init__(self, name:str,
                 # params for class
                 # params for parent
                 enabled:Optional[Set[ExtractionMode]]=None, type_name:Optional[str]=None, description:Optional[str]=None,
                 # dict of leftovers
                 other_elements:Optional[Map]=None
        ):
        unparsed_elements : Map = other_elements or {}

        super().__init__(name=name, enabled=enabled, type_name=type_name, description=description, other_elements=unparsed_elements)

    @property
    def AsMarkdown(self) -> str:
        ret_val   : str

        ret_val = f"**{self.Name}** : *Detector* {' (disabled)' if not ExtractionMode.DETECTOR in self.Enabled else ''}  \n{self.Description}  \n"
        if len(self.NonStandardElements) > 0:
            ret_val += "*Other elements*:  \n\n" + "\n".join([f"{elem_name} : {elem}" for elem_name,elem in self.NonStandardElements.items()])
        return ret_val

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Dict[str, Any])-> "DetectorConfig":
        """_summary_

        TODO : Add example of what format unparsed_elements is expected to have.

        :param name: _description_
        :type name: str
        :param unparsed_elements: _description_
        :type unparsed_elements: Dict[str, Any]
        :return: _description_
        :rtype: DetectorConfig
        """
        return DetectorConfig(name=name, other_elements=unparsed_elements)

    @classmethod
    def Default(cls) -> "DetectorConfig":
        return DetectorConfig(name="DefaultDetectorConfig", other_elements={})
