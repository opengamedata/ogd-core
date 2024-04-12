# import standard libraries
from typing import Any, Dict, List
# import local files
from ogd.core.schemas.games.FeatureSchema import FeatureSchema

class AggregateSchema(FeatureSchema):
    def __init__(self, name:str, all_elements:Dict[str, Any]):
        super().__init__(name=name, all_elements=all_elements)

    @property
    def AsMarkdown(self) -> str:
        ret_val   : str

        ret_val = f"**{self.Name}** : *{self.ReturnType}*, *Aggregate feature* {' (disabled)' if not len(self.Enabled) > 0 else ''}  \n{self.Description}  \n"
        if len(self.Subfeatures) > 0:
            ret_val += "*Sub-features*:  \n\n" + "\n".join([subfeature.AsMarkdown for subfeature in self.Subfeatures.values()])
        if len(self.NonStandardElements) > 0:
            ret_val += "*Other elements*:  \n\n" + "\n".join([f"{elem_name} : {elem}" for elem_name,elem in self.NonStandardElements.items()])
        return ret_val
