# import standard libraries
from typing import Any, Dict # , overload
# import local files
from ogd.core.schemas.Schema import Schema


class CredentialSchema(Schema):
    """Dumb struct to contain data pertaining to credentials for accessing a data source.

    In general, a credential can have a key, or a user-password combination
    """
    # @overload
    # def __init__(self, name:str, other_elements:Dict[str, Any]): ...

    def __init__(self, name:str, unparsed_elements:Dict[str, Any] | Any):
        super().__init__(name=name, other_elements=unparsed_elements)
