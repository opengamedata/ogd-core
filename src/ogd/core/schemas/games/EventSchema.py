# import standard libraries
import logging
from typing import Any, Dict, Optional
# import local files
from ogd.core.schemas.games.DataElementSchema import DataElementSchema
from ogd.core.schemas.Schema import Schema
from ogd.core.utils.Logger import Logger

class EventSchema(Schema):
    """
    Dumb struct to contain a specification of an Event in a GameSchema file.

    These essentially are just a description of the event, and a set of elements in the EventData attribute of the Event.
    """
    def __init__(self, name:str, all_elements:Dict[str, Dict]):
        self._description : str                               = "No description available"
        self._event_data  : Dict[str, DataElementSchema] = {}

        if not isinstance(all_elements, dict):
            all_elements = {}
            Logger.Log(f"For {name} Event config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        if "description" in all_elements.keys():
            self._description = EventSchema._parseDescription(description=all_elements['description'])
        else:
            self._description = "Unknown"
            Logger.Log(f"{name} EventSchema config does not have a 'description' element; defaulting to description='{self._description}", logging.WARN)
        if "event_data" in all_elements.keys():
            self._event_data = EventSchema._parseEventDataElements(event_data=all_elements['event_data'])
        else:
            self._event_data = {}
            Logger.Log(f"{name} EventSchema config does not have an 'event_data' element; defaulting to empty dict", logging.WARN)
        _leftovers = { key : val for key,val in all_elements.items() if key not in {"description", "event_data"} }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def Description(self) -> str:
        return self._description

    @property
    def EventData(self) -> Dict[str, DataElementSchema]:
        return self._event_data

    @property
    def AsMarkdown(self) -> str:
        return "\n\n".join([
            f"### **{self.Name}**",
            self.Description,
            "#### Event Data",
            "\n".join(
                  [elem.AsMarkdown for elem in self.EventData.values()]
                + (["- Other Elements:"] +
                   [f"  - **{elem_name}**: {elem_desc}" for elem_name,elem_desc in self.NonStandardElements]
                  ) if len(self.NonStandardElements) > 0 else []
            )
        ])

    @property
    def AsMarkdownTable(self) -> str:
        ret_val = [
            f"### **{self.Name}**",
            f"{self.Description}",
            "#### Event Data",
            "\n".join(
                ["| **Name** | **Type** | **Description** | **Sub-Elements** |",
                 "| ---      | ---      | ---             | ---         |"]
              + [elem.AsMarkdownRow for elem in self.EventData.values()]
            ),
        ]
        if len(self.NonStandardElements) > 0:
            ret_val.append("#### Other Elements")
            ret_val.append(
                "\n".join( [f"- **{elem_name}**: {elem_desc}  " for elem_name,elem_desc in self.NonStandardElements] )
            )
        return "\n\n".join(ret_val)

    @staticmethod
    def _parseEventDataElements(event_data):
        ret_val : Dict[str, DataElementSchema]
        if isinstance(event_data, dict):
            ret_val = {name:DataElementSchema(name=name, all_elements=elems) for name,elems in event_data.items()}
        else:
            ret_val = {}
            Logger.Log(f"event_data was unexpected type {type(event_data)}, defaulting to empty dict.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDescription(description):
        ret_val : str
        if isinstance(description, str):
            ret_val = description
        else:
            ret_val = str(description)
            Logger.Log(f"Event description was not a string, defaulting to str(description) == {ret_val}", logging.WARN)
        return ret_val
