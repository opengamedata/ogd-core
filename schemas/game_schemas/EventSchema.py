# import standard libraries
import logging
from typing import Any, Dict, List
# import local files
from utils import Logger

class EventDataElementSchema:
    def __init__(self, name:str, all_elements:Dict[str, str]):
        self._name     : str
        self._elements : Dict[str, str]
        if isinstance(all_elements, dict):
            if "type" in all_elements.keys():
                self._type = EventSchema._parseEventType(all_elements['return_type'])
            else:
                pass
            if "description" in all_elements.keys():
                pass
            else:
                pass
            if "details" in all_elements.keys():
                pass
            else:
                pass
            self._elements = all_elements

class EventSchema:
    def __init__(self, name:str, all_elements:Dict[str, Dict]):
        self._name        : str
        self._description : str
        self._event_data  : Dict[str, EventDataElementSchema]
        self._elements    : Dict[str, Any]

        if type(name) == str:
            self._name = name
        else:
            self._name = str(name)
            Logger.Log(f"Event name was not a string, defaulting to str(name) == {self._name}", logging.WARN)
        if not isinstance(all_elements, dict):
            self._elements   = {}
            Logger.Log(f"For {name} Event config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        if "description" in all_elements.keys():
            self._description = EventSchema._parseDescription(description=all_elements['description'])
        else:
            pass
        if "event_data" in all_elements.keys():
            self._event_data = EventSchema._parseEventDataElements(event_data=all_elements['event_data'])
        else:
            pass
        self._elements = { key : val for key,val in all_elements.items() if key not in {"description", "event_data"} }

    @property
    def Name(self) -> str:
        return self._name

    @property
    def EventData(self) -> Dict[str, EventDataElementSchema]:
        return self._event_data

    @property
    def Elements(self) -> Dict[str, Any]:
        return self._elements

    @property
    def ElementNames(self) -> List[str]:
        return list(self._elements.keys())

    @property
    def AsMarkdown(self) -> str:
        return "\n".join([f"**{self.Name}**:  "] + [f"- **{elem_name}**: {elem_desc}  " for elem_name,elem_desc in self.Elements])

    @staticmethod
    def _parseEventDataElements(event_data):
        ret_val : Dict[str, EventDataElementSchema]
        if isinstance(event_data, dict):
            ret_val = {name:EventDataElementSchema(name=name, all_elements=elems) for name,elems in event_data.items()}
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
