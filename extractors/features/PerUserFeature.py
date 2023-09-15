# import locals
from extractors.Extractor import ExtractorParameters
from extractors.features.PerCountFeature import PerCountFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode

## @class PerLevelFeature
class PerUserFeature(PerCountFeature):
    """PerLevelFeature
    Abstract base class for per-user game features.
    Works like a normal Feature, but checks if the given event has right user
    before attempting to extract from event.

    Args:
        Feature (_type_): PerLevelFeature is a subclass of Feature

    Returns:
        _type_: _description_
    """

    # *** BUILT-INS ***

    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _validateEventCountIndex(self, event:Event):
    
        return event.UserID == self.CountIndex
