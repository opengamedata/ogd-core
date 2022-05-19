import json
from typing import Any, Dict, Union

class Coder:
    def __init__(self, name:str, id:str):
        self._name = name
        self._id   = id

    @staticmethod
    def FromJSON(json_obj:Dict[str, Any]):
        _name : Union[str, None] = json_obj.get("name", None)
        _id   : Union[str, None] = json_obj.get("id", None)
        if _name is None:
            raise ValueError("JSON object for Coder has no 'name' element!")
        elif _id is None:
            raise ValueError("JSON object for Coder has no 'id' element!")
        else:
            return Coder(name=_name, id=_id)

    @property
    def Name(self) -> str:
        return self._name

    @property
    def ID(self) -> str:
        return self._id

    @property
    def JSON(self) -> str:
        return json.dumps({
            "name":self.Name,
            "id":self.ID
        })
