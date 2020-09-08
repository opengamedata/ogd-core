## import standard libraries
import abc
import typing
from typing import List, Dict, Any
import logging
## import local libraries
from models.Model import *

## @class FeatureModel
#  Abstract base class for models that use per-session feature data as input rows.
#  For these models, we wrap the functionality in a private _eval function, which is called once per row.
#
class SequenceModel(Model):
    def __init__(self, levels: typing.List[int] = []):
        super().__init__(levels=levels, input_type=ModelInputType.SEQUENCE)

    def Eval(self, rows: typing.List) -> typing.List:
        return self._eval(rows)

    ## Abstract declaration of a function to perform calculation of a model results from a row.
    #
    #  @param rows : A list of rows of data for a session, which should each be a mapping of column names to values.
    #  row keys include:
    #  id, app_id, app_id_fast, app_version, sess_id, persistent_sess_id, player_id, level, event,
    #  event_custom, event_data_simple, event_data_complex, client_time, client_secs_ms, server_time, remote_addr,
    #  req_id, sess_n, http_user_agent
    #  @return     : A result for the given row of data
    @abc.abstractmethod
    def _eval(self, rows: List[Dict[str, Any]]) -> Any:
        pass