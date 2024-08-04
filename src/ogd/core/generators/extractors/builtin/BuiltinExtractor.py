## import standard libraries
import abc
import logging
from typing import Any, Dict, List, Optional, Type
# import locals
from ogd.core.generators.Generator import Generator, GeneratorParameters
from ogd.core.generators.extractors.Extractor import Extractor

## @class BuiltinGenerator
class BuiltinExtractor(Extractor):

    # *** ABSTRACTS ***

    ## Abstract function to get a list of event types the Feature wants.
    @classmethod
    @abc.abstractmethod
    def _createDerivedGenerator(cls, params:GeneratorParameters, schema_args:Dict[str,Any]) -> Type["BuiltinExtractor"]:
        """ Abstract function to generate a derived version of the Generator subclass, using the schema args.
            In general, this should just be a matter of creating a type that overwrites the list of events in `_eventFilter` or similar,
            but subclasses are left a lot of leeway in what they change about the derived type.

        :return: [description]
        :rtype: List[str]
        """
        raise TypeError(f"Can't call function on class {cls.__name__} with abstract method _eventFilter")

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, params:GeneratorParameters, schema_args:Dict[str,Any]):
        super().__init__(params=params)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
