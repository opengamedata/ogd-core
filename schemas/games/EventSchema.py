# import standard libraries
import logging
from typing import Any, Dict, List, Optional
# import local files
from schemas.Schema import Schema
from utils.Logger import Logger

class EventDataElementSchema(Schema):
    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._type        : str
        self._description : str
        self._details     : Optional[Dict[str, str]]

        if not isinstance(all_elements, dict):
            if isinstance(all_elements, str):
                all_elements = { 'description' : all_elements }
                Logger.Log(f"For {name} EventDataElement config, all_elements was a str, probably in legacy format. Defaulting to all_elements = {'{'} description : {all_elements['description']} {'}'}", logging.WARN)
            else:
                all_elements = {}
                Logger.Log(f"For {name} EventDataElement config, all_elements was not a dict, defaulting to empty dict", logging.WARN)

        if "type" in all_elements.keys():
            self._type = EventDataElementSchema._parseElementType(all_elements['type'])
        else:
            self._type = "Unknown"
            Logger.Log(f"{name} EventDataElement config does not have a 'type' element; defaulting to type='{self._type}", logging.WARN)
        if "description" in all_elements.keys():
            self._description = EventDataElementSchema._parseDescription(all_elements['description'])
        else:
            self._description = "Unknown"
            Logger.Log(f"{name} EventDataElement config does not have a 'description' element; defaulting to description='{self._description}", logging.WARN)
        if "details" in all_elements.keys():
            self._details = EventDataElementSchema._parseDetails(details=all_elements['details'])
        else:
            self._details = None
        _leftovers = { key : val for key,val in all_elements.items() if key not in {"type", "description", "details"} }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = f"- **{self.Name}** : *{self.ElementType}*, {self.Description}"
        if self.Details is not None:
            detail_markdown = [f"**{name}** - {desc}" for name,desc in self.Details]
            ret_val += f"\n  Details: {detail_markdown}\n"
        return ret_val

    @property
    def ElementType(self) -> str:
        return self._type

    @property
    def Description(self) -> str:
        return self._description

    @property
    def Details(self) -> Optional[Dict[str, str]]:
        return self._details
    
    @staticmethod
    def _parseElementType(event_type):
        ret_val : str
        if isinstance(event_type, str):
            ret_val = event_type
        else:
            ret_val = str(event_type)
            Logger.Log(f"EventDataElement type was not a string, defaulting to str(type) == {ret_val}", logging.WARN)
        return ret_val
    
    @staticmethod
    def _parseDescription(description):
        ret_val : str
        if isinstance(description, str):
            ret_val = description
        else:
            ret_val = str(description)
            Logger.Log(f"EventDataElement description was not a string, defaulting to str(description) == {ret_val}", logging.WARN)
        return ret_val
    
    @staticmethod
    def _parseDetails(details):
        ret_val : Dict[str, str] = {}
        if isinstance(details, dict):
            for key,val in details.items():
                if isinstance(key, str):
                    if isinstance(val, str):
                        ret_val[key] = val
                    else:
                        ret_val[key] = str(val)
                        Logger.Log(f"EventDataElement detail value for key {key} was unexpected type {type(val)}, defaulting to str(val) == {ret_val[key]}", logging.WARN)
                else:
                    _key = str(key)
                    Logger.Log(f"EventDataElement detail key was unexpected type {type(key)}, defaulting to str(key) == {_key}", logging.WARN)
                    if isinstance(val, str):
                        ret_val[_key] = val
                    else:
                        ret_val[_key] = str(val)
                        Logger.Log(f"EventDataElement detail value for key {_key} was unexpected type {type(val)}, defaulting to str(val) == {ret_val[_key]}", logging.WARN)
        else:
            ret_val = {}
            Logger.Log(f"EventDataElement details was not a dict, defaulting to empty dict.", logging.WARN)
        return ret_val

class EventSchema(Schema):
    def __init__(self, name:str, all_elements:Dict[str, Dict]):
        self._description : str
        self._event_data  : Dict[str, EventDataElementSchema]

        if not isinstance(all_elements, dict):
            self._elements   = {}
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
    def EventData(self) -> Dict[str, EventDataElementSchema]:
        return self._event_data

    @property
    def AsMarkdown(self) -> str:
        summary = [f"**{self.Name}**: {self.Description}"]
        event_data = [elem.AsMarkdown for elem in self.EventData.values()]
        other_data_desc = [f"- Other Elements:"]
        other_data = [f"  - **{elem_name}**: {elem_desc}  " for elem_name,elem_desc in self.NonStandardElements]
        return "\n".join(summary + event_data + other_data_desc + other_data)

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
