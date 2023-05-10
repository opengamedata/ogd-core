# import standard libraries
import abc
import logging
from typing import Any, Dict, Optional, Type
# import local files
from schemas.Schema import Schema
from schemas.configs.data_sources.BigQuerySourceSchema import BigQuerySchema
from schemas.configs.data_sources.FileSourceSchema import FileSourceSchema
from schemas.configs.data_sources.MySQLSourceSchema import MySQLSchema

class DataSourceSchema(Schema):
    def __init__(self, name:str, other_elements:Dict[str, Any]):
        super().__init__(name=name, other_elements=other_elements)

    @property
    @abc.abstractmethod
    def Type(self) -> str:
        pass
