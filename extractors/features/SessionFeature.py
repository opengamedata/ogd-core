# import standard libraries
import logging
# import locals
from extractors.features.Feature import Feature
from extractors.Extractor import ExtractorParameters
from utils import Logger

class SessionFeature(Feature):

    # *** BUILT-INS ***

    def __init__(self, params:ExtractorParameters):
        if params._count_index != 0:
            Logger.Log(f"Session feature {params._name} got non-zero count index of {params._count_index}!", logging.WARN)
        params._count_index = 0
        super().__init__(params=params)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
