# import standard libraries
import logging
# import locals
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.utils.Logger import Logger

class SessionFeature(Feature):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, params:GeneratorParameters):
        if params._count_index is not None and params._count_index != 0:
            Logger.Log(f"Session feature {params._name} got non-zero count index of {params._count_index}!", logging.WARN)
        params._count_index = 0
        super().__init__(params=params)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
