# import locals
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.games.ICECUBE.DBExport import scenes_list
## @class PerLevelFeature
class PerSceneFeature(PerCountFeature):
    """PerLevelFeature
    Abstract base class for per-level game features.
    Works like a normal Feature, but checks if the given event has right "level"
    before attempting to extract from event.

    Args:
        Feature (_type_): PerLevelFeature is a subclass of Feature

    Returns:
        _type_: _description_
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _validateEventCountIndex(self, event:Event):
        return event.EventData['scene_name'] == scenes_list[self.CountIndex]