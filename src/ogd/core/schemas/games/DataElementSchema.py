# import standard libraries
import logging
from typing import Any, Dict, List, Optional
# import local files
from ogd.core.schemas.Schema import Schema
from ogd.core.utils.Logger import Logger

class DataElementSchema(Schema):
    """
    Dumb struct to contain a specification of a data element from the EventData, GameState, or UserData attributes of an Event.
    """
    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._type        : str
        self._description : str
        self._details     : Optional[Dict[str, str]]

        if not isinstance(all_elements, dict):
            if isinstance(all_elements, str):
                all_elements = { 'description' : all_elements }
                Logger.Log(f"For EventDataElement config of `{name}`, all_elements was a str, probably in legacy format. Defaulting to all_elements = {'{'} description : {all_elements['description']} {'}'}", logging.WARN)
            else:
                all_elements = {}
                Logger.Log(f"For EventDataElement config of `{name}`, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        if "type" in all_elements.keys():
            self._type = DataElementSchema._parseElementType(all_elements['type'])
        else:
            self._type = "Unknown"
            Logger.Log(f"{name} EventDataElement config does not have a 'type' element; defaulting to type='{self._type}", logging.WARN)
        if "description" in all_elements.keys():
            self._description = DataElementSchema._parseDescription(all_elements['description'])
        else:
            self._description = "Unknown"
            Logger.Log(f"{name} EventDataElement config does not have a 'description' element; defaulting to description='{self._description}", logging.WARN)
        if "details" in all_elements.keys():
            self._details = DataElementSchema._parseDetails(details=all_elements['details'])
        else:
            self._details = None
        _leftovers = { key : val for key,val in all_elements.items() if key not in {"type", "description", "details"} }
        super().__init__(name=name, other_elements=_leftovers)

    @property
    def AsMarkdown(self) -> str:
        ret_val : str = f"- **{self.Name}** : *{self.ElementType}*, {self.Description}"
        if self.Details is not None:
            detail_markdowns = [f"    - **{name}** - {desc}  " for name,desc in self.Details.items()]
            detail_joined = '\n'.join(detail_markdowns)
            ret_val += f"  \n  Details:  \n{detail_joined}"
        return ret_val

    @property
    def AsMarkdownRow(self) -> str:
        ret_val : str = f"| {self.Name} | {self.ElementType} | {self.Description} |"
        if self.Details is not None:
            detail_markdowns = [f"**{name}** : {desc}" for name,desc in self.Details.items()]
            ret_val += ', '.join(detail_markdowns)
        ret_val += " |"
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
