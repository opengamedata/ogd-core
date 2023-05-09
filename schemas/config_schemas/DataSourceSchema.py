# import standard libraries
import abc
import logging
from typing import Any, Dict, Optional, Type
# import local files
from schemas.Schema import Schema
from schemas.config_schemas.BigQuerySourceSchema import BigQuerySchema
from schemas.config_schemas.MySQLSourceSchema import MySQLSchema

class DataSourceSchema(Schema):
    def __init__(self, name:str, other_elements:Dict[str, Any]):
        super().__init__(name=name, other_elements=other_elements)

    @property
    @abc.abstractmethod
    def Type(self) -> str:
        pass

def ParseSourceType(all_elements:Dict[str, Any]) -> Optional[Type[DataSourceSchema]]:
    match (all_elements.get("DB_TYPE", "").upper()):
        case "BIGQUERY":
            return BigQuerySchema
        case "MYSQL":
            return MySQLSchema
        case _:
            return None
