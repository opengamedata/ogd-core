# import standard libraries
import abc
from multiprocessing.sharedctypes import Value
# import locals
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.models.Event import Event

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

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    @property
    def CountIndex(self) -> int:
        _ci = super().CountIndex
        if _ci is None:
            raise ValueError(f"PerCountFeature of type {type(self)} was given a null CountIndex!")
        else:
            return _ci

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _validateEvent(self, event:Event):
       
        return (
            self._validateVersion(event.LogVersion)
        and self._validateEventType(event_type=event.EventName)
        and self._validateEventCountIndex(event=event)
        )
