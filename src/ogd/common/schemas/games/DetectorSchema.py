# import standard libraries
from typing import Any, Dict
# import local files
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.schemas.games.ExtractorSchema import ExtractorSchema

class DetectorSchema(ExtractorSchema):
    def __init__(self, name:str, all_elements:Dict[str, Any]):
        super().__init__(name=name, all_elements=all_elements)

    @property
    def AsMarkdown(self) -> str:
        ret_val   : str

        ret_val = f"**{self.Name}** : *Detector* {' (disabled)' if not ExtractionMode.DETECTOR in self.Enabled else ''}  \n{self.Description}  \n"
        if len(self.NonStandardElements) > 0:
            ret_val += "*Other elements*:  \n\n" + "\n".join([f"{elem_name} : {elem}" for elem_name,elem in self.NonStandardElements.items()])
        return ret_val