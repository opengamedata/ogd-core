## import standard libraries
import abc
import typing
from typing import Any, Dict, List, Tuple, Union
# Local imports
from schemas.GameSchema import GameSchema
from schemas.Event import Event

## @class Extractor
class Extractor(abc.ABC):

    # *** ABSTRACTS ***

    ## Abstract function to get a list of event types the Feature wants.
    @abc.abstractmethod
    def LoadFeatures(self, schema:GameSchema) -> None:
        pass

    ## Abstract declaration of a function to get the names of all features.
    @abc.abstractmethod
    def GetFeatureNames(self) -> List[str]:
        pass

    ## Abstract declaration of a function to get the calculated value of the feature, given data seen so far.
    @abc.abstractmethod
    def GetFeatureValues(self) -> List[Any]:
        pass

    ## Abstract declaration of a function to get the calculated value of the feature, given data seen so far.
    @abc.abstractmethod
    def ProcessEvent(self, event: Event):
        pass

    # *** PUBLIC BUILT-INS ***

    def __init__(self):
        pass

    def __str__(self):
        return f""

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
