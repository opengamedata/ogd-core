## import standard libraries
import abc
from enum import IntEnum
from typing import Dict, List, Tuple, Optional

# import local files
from coding.Code import Code
from coding.Coder import Coder
from interfaces.Interface import Interface
from schemas.IDMode import IDMode
from utils import Logger

class CodingInterface(Interface):
    class RetrievalMode(IntEnum):
        BY_GAME    = 1
        BY_CODER   = 2
        BY_SESSION = 3

    # *** ABSTRACTS ***

    @abc.abstractmethod
    def _allCoders(self) -> Optional[List[Coder]]:
        pass

    @abc.abstractmethod
    def _createCoder(self, coder_id:str) -> bool:
        pass

    @abc.abstractmethod
    def _getCodeWordsBySession(self, session_id:str) -> Optional[List[str]]:
        pass

    @abc.abstractmethod
    def _getCodeWordsByCoder(self, coder_id:str) -> Optional[List[str]]:
        pass

    @abc.abstractmethod
    def _getCodeWordsByGame(self, session_id:str) -> Optional[List[str]]:
        pass

    @abc.abstractmethod
    def _getCodesBySession(self, session_id:str) -> Optional[List[Code]]:
        pass

    @abc.abstractmethod
    def _getCodesByCoder(self, coder_name:str) -> Optional[List[Code]]:
        pass

    @abc.abstractmethod
    def _createCode(self, code:str, coder:Coder, events:List[Code.EventID], notes:Optional[str]=None):
        pass

    # *** PUBLIC BUILT-INS ***

    def __init__(self, game_id):
        super().__init__()
        self._game_id : str  = game_id

    def __del__(self):
        self.Close()

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def AllCoders(self) -> Optional[List[Coder]]:
        ret_val = None
        if self.IsOpen():
            ret_val = self._allCoders()
        else:
            Logger.Log("Can't retrieve list of all Coders, the source interface is not open!")
        return ret_val

    def CreateCoder(self, coder_name:str) -> bool:
        ret_val = False
        if self.IsOpen():
            ret_val = self._createCoder(coder_id=coder_name)
        else:
            Logger.Log("Can't create Coder, the source interface is not open!")
        return ret_val

    def GetCodeWords(self, mode:RetrievalMode, id:str):
        if mode == CodingInterface.RetrievalMode.BY_CODER:
            self._getCodeWordsByCoder(coder_id=id)

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
