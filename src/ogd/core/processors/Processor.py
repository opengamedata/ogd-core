## import standard libraries
import abc
import json
from datetime import datetime
from typing import List
# import locals
from ogd.core.configs.generators.GeneratorCollectionConfig import GeneratorCollectionConfig
from ogd.common.models.Event import Event
from ogd.common.utils.typing import ExportRow

## @class Processor
class Processor(abc.ABC):

    # *** ABSTRACTS ***

    ## Abstract declaration of a function to get the calculated value of the feature, given data seen so far.
    @abc.abstractmethod
    def _processEvent(self, event:Event) -> None:
        pass

    @abc.abstractmethod
    def _getLines(self) -> List[ExportRow]:
        pass

    @abc.abstractmethod
    def _clearLines(self) -> None:
        pass

    # *** BUILT-INS ***

    def __init__(self, generator_cfg:GeneratorCollectionConfig):
        self._generator_cfg : GeneratorCollectionConfig = generator_cfg

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def ProcessEvent(self, event:Event) -> None:
        # TODO: add error handling code, if applicable.
        self._processEvent(event=event)
    
    @property
    def Lines(self) -> List[ExportRow]:
        ret_val : List[ExportRow] = []

        # TODO: Should do list of events instead, and put it on outerface to do this part.
        # When retrieving lines, ensure all lines have values in appropriate format for output to file/web response/whatever.
        _dumps_default = lambda x : x.isoformat() if isinstance(x, datetime) else str(x)
        ret_val = [[json.dumps(_col, default=_dumps_default) for _col in _line] for _line in self._getLines()]

        return ret_val

    def ClearLines(self):
        self._clearLines()

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
