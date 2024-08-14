# import standard libraries
from typing import Any, Dict
# import local files
from ogd.core.schemas.configs.data_sources.DataSourceSchema import DataSourceSchema

class FileSourceSchema(DataSourceSchema):
    def __init__(self, name:str, all_elements:Dict[str, Any]):
        super().__init__(name=name, other_elements=all_elements)

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"FILE SOURCE"
        return ret_val

    @property
    def AsConnectionInfo(self) -> str:
        ret_val : str = f"{self._name}"
        return ret_val
