# Local imports
from features.Feature import Feature
from schemas.Event import Event

## @class PerLevelFeature
#  Abstract base class for per-level game features.
#  Works like a normal Feature, but checks if the given event has right "level"
#  before attempting to extract from event.
class PerLevelFeature(Feature):
    def __init__(self, name:str, description:str, count_index:int):
        Feature.__init__(self, name=name, description=description, count_index=count_index)

    def _validateEvent(self, event:Event):
        return (
            self._validateVersion(event.app_version)
        and self._validateEventType(event_type=event.event_name)
        and self._validateEventLevel(level=event.event_data['level'])
        )

    def _validateEventLevel(self, level:int):
        return level == self._count_index