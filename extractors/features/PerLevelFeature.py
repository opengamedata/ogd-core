# import locals
from extractors.features.PerCountFeature import PerCountFeature
from schemas.Event import Event

## @class PerLevelFeature
class PerLevelFeature(PerCountFeature):
    """PerLevelFeature
    Abstract base class for per-level game features.
    Works like a normal Feature, but checks if the given event has right "level"
    before attempting to extract from event.

    Args:
        Feature (_type_): PerLevelFeature is a subclass of Feature

    Returns:
        _type_: _description_
    """

    # *** BUILT-INS ***

    def __init__(self, name:str, description:str, count_index:int):
        super().__init__(name=name, description=description, count_index=count_index)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _validateEventCountIndex(self, event:Event):
        return event.EventData['level'] == self.CountIndex