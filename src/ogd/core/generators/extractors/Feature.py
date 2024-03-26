## import standard libraries
import abc
from typing import Any, Dict, List, Optional
# import locals
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Extractor import Extractor

## @class Model
#  Abstract base class for session-level Wave features.
#  Models only have one public function, called Eval.
#  The Eval function takes a list of row data, computes some statistic, and returns a list of results.
#  If the model works on features from session data, it should calculate one result for each row (each row being a session).
#  If the model works on a raw list of recent events, it should calculate a single result (each row being an event).
class Feature(Extractor):
    """
    Simple wrapper for the Extractor base class.
    
    Created for compatibility with existing feature extractors that use Feature as their base.
    as the same functions as Extractor class
    """
    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)

