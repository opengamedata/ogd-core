import abc
import traceback
import typing
import pandas as pd
## import local files
import utils
from GameTable import GameTable
from interfaces.MySQLInterface import SQL
from schemas.Schema import Schema

class DataManager(abc.ABC):
    def __init__(self, game_id):
        self._game_id = game_id

    ## Abstract method to retrieve the data for a given set of ids.
    #  the request.
    @abc.abstractmethod
    def RetrieveSliceData(self, id_list) -> typing.List[typing.Tuple]:
        pass
