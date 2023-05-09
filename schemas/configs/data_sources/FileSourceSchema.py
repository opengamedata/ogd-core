# import standard libraries
import abc
import logging
from typing import Any, Dict, Optional, Type
# import local files
from schemas.Schema import Schema
from schemas.configs.data_sources.DataSourceSchema import DataSourceSchema
from utils import Logger

class FileSourceSchema(DataSourceSchema):
    def __init__(self, name:str, all_elements:Dict[str, Any]):
        super().__init__(name=name, other_elements=all_elements)

    @property
    def Type(self) -> str:
        return "File"

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"FILE SOURCE"
        return ret_val
