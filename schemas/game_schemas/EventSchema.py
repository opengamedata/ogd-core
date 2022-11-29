# import standard libraries
import logging
from typing import Dict, List, Optional
# import local files
from utils import Logger

class ElementDetailSchema:
    def __init__(self, name:str, type_name:str):
        self._name        : str
        self._type_name   : str

        self._name = ElementDetailSchema._parseName(name)
        self._type_name = ElementDetailSchema._parseType(type_name)

    @property
    def Name(self) -> str:
        return self._name

    @property
    def TypeName(self) -> str:
        return self._type_name

    @property
    def AsMarkdown(self) -> str:
        return f"**{self.Name}** :  *{self.TypeName}*  \n"
    
    @staticmethod
    def _parseName(name):
        ret_val : str
        if isinstance(name, str):
            ret_val = name
        else:
            ret_val = str(name)
            Logger.Log(f"ElementDetail name was not a string, defaulting to str(name) == {ret_val}", logging.WARN)
        return ret_val
    
    @staticmethod
    def _parseType(extractor_type):
        ret_val : str
        if isinstance(extractor_type, str):
            ret_val = extractor_type
        else:
            ret_val = str(extractor_type)
            Logger.Log(f"ElementDetail type was not a string, defaulting to str(type) == {ret_val}", logging.WARN)
        return ret_val

class EventElementSchema:
    def __init__(self, name:str, all_elements:Dict[str, str]):
        self._name        : str
        self._type_name   : str
        self._description : str
        self._details     : Dict[str, ElementDetailSchema]
        self._elements    : Dict[str, str]

        self._name = EventSchema._parseName(name)
        if isinstance(all_elements, dict):
            if "type" in all_elements.keys():
                self._type_name = EventElementSchema._parseType(all_elements['type'])
            else:
                self._type_name = self._name

            if "description" in all_elements.keys():
                self._description = EventElementSchema._parseDescription(all_elements['description'])
            else:
                self._description = ""
                Logger.Log(f"{name} config does not have an 'description' element; defaulting to description=''", logging.WARN)

            if "details" in all_elements.keys():
                self._details = EventElementSchema._parseDetails(all_elements['details'])
            else:
                self._details = {}

            self._elements = { key : val for key,val in all_elements.items() if key not in {"type", "description", "details"} }
        else:
            self._type_name = "UNKNOWN"
            self._description = "No Description"
            self._details = {}
            self._elements = {}
            Logger.Log(f"For {name} EventElement config, all_elements was not a dictionary. Using defaults.", logging.WARN)

    @property
    def Name(self) -> str:
        return self._name

    @property
    def TypeName(self) -> str:
        return self._type_name

    @property
    def Description(self) -> str:
        return self._description

    @property
    def Details(self) -> Dict[str, ElementDetailSchema]:
        return self._details

    @property
    def Elements(self) -> Dict[str, str]:
        return self._elements

    @property
    def ElementNames(self) -> List[str]:
        return list(self._elements.keys())

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"**{self.Name}** :  *{self.TypeName}*, {self.Description}  \n"
        if len(self.Details) > 0:
            ret_val += "*Details*:  \n\n" + "\n".join([detail.AsMarkdown for detail in self.Details.values()])
        if len(self.Elements) > 0:
            ret_val += "*Other elements*:  \n\n" + "\n".join([f"{elem_name} - {elem}" for elem_name,elem in self.Elements.items()])

        return ret_val
    
    @staticmethod
    def _parseName(name):
        ret_val : str
        if isinstance(name, str):
            ret_val = name
        else:
            ret_val = str(name)
            Logger.Log(f"EventElement name was not a string, defaulting to str(name) == {ret_val}", logging.WARN)
        return ret_val
    
    @staticmethod
    def _parseType(extractor_type):
        ret_val : str
        if isinstance(extractor_type, str):
            ret_val = extractor_type
        else:
            ret_val = str(extractor_type)
            Logger.Log(f"EventElement type was not a string, defaulting to str(type) == {ret_val}", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDescription(description):
        ret_val : str
        if isinstance(description, str):
            ret_val = description
        else:
            ret_val = str(description)
            Logger.Log(f"EventElement description was not a string, defaulting to str(description) == {ret_val}", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDetails(details) -> Dict[str, ElementDetailSchema]:
        ret_val : Dict[str, ElementDetailSchema]
        if isinstance(details, dict):
            ret_val = { name : ElementDetailSchema(name, elem_type) for name, elem_type in details.items() }
        else:
            ret_val = {}
            Logger.Log(f"EventElement details was not a dict, defaulting to empty dictionary.", logging.WARN)
        return ret_val

class EventSchema:
    def __init__(self, name:str, all_elements:Dict[str, str]):
        self._name        : str
        self._description : str
        self._event_data  : Dict[str, EventElementSchema]
        self._elements    : Dict[str, str]

        self._name = EventSchema._parseName(name)
        if isinstance(all_elements, dict):
            if "description" in all_elements.keys():
                self._description = EventSchema._parseDescription(all_elements['description'])
            else:
                self._description = ""
                Logger.Log(f"{name} config does not have an 'description' element; defaulting to description=''", logging.WARN)
            if "event_data" in all_elements.keys():
                self._event_data = EventSchema._parseData(all_elements['event_data'])
            else:
                self._event_data = {}
                Logger.Log(f"{name} config does not have an 'event_data' element; defaulting to empty dictionary", logging.WARN)
            self._elements = { key : val for key,val in all_elements.items() if key not in {"event_data", "description"} }
        else:
            self._description = "No Description"
            self._event_data = {}
            self._elements = {}
            Logger.Log(f"For {name} Event config, all_elements was not a dictionary. Using defaults.", logging.WARN)

    @property
    def Name(self) -> str:
        return self._name

    @property
    def Description(self) -> str:
        return self._description

    @property
    def EventData(self) -> Dict[str, EventElementSchema]:
        return self._event_data

    @property
    def Elements(self) -> Dict[str, str]:
        return self._elements

    @property
    def ElementNames(self) -> List[str]:
        return list(self._elements.keys())

    @property
    def AsMarkdown(self) -> str:
        ret_val : str
        
        ret_val = f"**{self.Name}**: {self.Description}"
        if len(self.EventData) > 0:
            ret_val += "`event_data`:  \n\n" + "\n".join([datum.AsMarkdown for datum in self.EventData.values()])
        if len(self.Elements) > 0:
            ret_val += "*Other elements*:  \n\n" + "\n".join([f"{elem_name} - {elem}" for elem_name,elem in self.Elements.items()])

        return ret_val
    
    @staticmethod
    def _parseName(name):
        ret_val : str
        if isinstance(name, str):
            ret_val = name
        else:
            ret_val = str(name)
            Logger.Log(f"Extractor name was not a string, defaulting to str(name) == {ret_val}", logging.WARN)
        return ret_val

    @staticmethod
    def _parseData(event_data):
        ret_val : Dict[str, EventElementSchema]
        if isinstance(event_data, dict):
            ret_val = { key : EventElementSchema(key, val) for key,val in event_data.items() }
        else:
            ret_val = {}
            Logger.Log(f"Extractor event_data was not a dict, defaulting to empty dictionary", logging.WARN)
        return ret_val

    @staticmethod
    def _parseDescription(description):
        ret_val : str
        if isinstance(description, str):
            ret_val = description
        else:
            ret_val = str(description)
            Logger.Log(f"Extractor description was not a string, defaulting to str(description) == {ret_val}", logging.WARN)
        return ret_val

