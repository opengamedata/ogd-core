# import standard libraries
import abc
from typing import Any, Dict
# import local files
from schemas.Schema import Schema

class DataSourceSchema(Schema):
    def __init__(self, name:str, other_elements:Dict[str, Any]):
        super().__init__(name=name, other_elements=other_elements)

    @property
    @abc.abstractmethod
    def Type(self) -> str:
        pass
