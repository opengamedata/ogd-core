## import standard libraries
import abc
import typing
## import locals
import utils

class DataInterface(abc.ABC):
    def __init__(self):
        self._is_open : bool = False

    def RetrieveFromIDs(self, ids: typing.List[int]) -> typing.List:
        if not self._is_open:
            utils.Logger.Log("Can't retrieve data, the source interface is not open!")
        else:
            return self._retrieveFromIDs(ids)

    @abc.abstractmethod
    def Open(self) -> None:
        pass

    @abc.abstractmethod
    def Close(self) -> None:
        pass

    @abc.abstractmethod
    def _retrieveFromIDs(self, ids: typing.List[int]) -> typing.List:
        pass