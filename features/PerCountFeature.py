# import standard libraries
import abc
# import locals
from features.Feature import Feature
from schemas.Event import Event

## @class PerLevelFeature
class PerCountFeature(Feature):
    """PerLevelFeature
    Abstract base class for per-level game features.
    Works like a normal Feature, but checks if the given event has right "level"
    before attempting to extract from event.

    Args:
        Feature (_type_): PerLevelFeature is a subclass of Feature

    Returns:
        _type_: _description_
    """

    # *** ABSTRACTS ***

    @abc.abstractmethod
    def _validateEventCountIndex(self, event:Event):
        pass

    # *** BUILT-INS ***

    def __init__(self, name:str, description:str, count_index:int):
        super().__init__(name=name, description=description, count_index=count_index)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _validateEvent(self, event:Event):
        return (
            self._validateVersion(event.LogVersion)
        and self._validateEventType(event_type=event.EventName)
        and self._validateEventCountIndex(event=event)
        )
