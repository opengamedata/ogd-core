## import standard libraries
import abc
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Union

# import local files
from schemas.IDMode import IDMode
from utils import Logger

class Interface(abc.ABC):

    # *** ABSTRACTS ***

    @abc.abstractmethod
    def _open(self) -> bool:
        pass

    @abc.abstractmethod
    def _close(self) -> bool:
        pass

    # *** PUBLIC BUILT-INS ***

    def __init__(self):
        self._is_open : bool = False

    def __del__(self):
        self.Close()

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def Open(self, force_reopen:bool = False) -> bool:
        if force_reopen or not self._is_open:
            return self._open()
        else:
            return True
    
    def IsOpen(self) -> bool:
        return True if self._is_open else False

    def Close(self) -> bool:
        if self.IsOpen():
            return self._close()
        else:
            return True

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
