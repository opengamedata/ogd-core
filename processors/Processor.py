## import standard libraries
import abc
import logging
from typing import Any, Dict, List, Type, Optional
# import locals
from schemas.FeatureData import FeatureData
from schemas.GameSchema import GameSchema
from schemas.Event import Event
from utils import Logger

## @class Processor
class Processor(abc.ABC):

    # *** ABSTRACTS ***

    ## Abstract declaration of a function to get the calculated value of the feature, given data seen so far.
    @abc.abstractmethod
    def _processEvent(self, event:Event) -> None:
        pass

    # *** BUILT-INS ***

    def __init__(self, game_schema: GameSchema, feature_overrides:Optional[List[str]]=None):
        self._game_schema : GameSchema            = game_schema

    def __str__(self):
        return f""

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def ProcessEvent(self, event:Event) -> None:
        # TODO: add error handling code, if applicable.
        self._processEvent(event=event)

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
