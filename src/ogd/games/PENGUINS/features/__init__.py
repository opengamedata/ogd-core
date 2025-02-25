"""Initializer for Penguins features"""

__all__ = [
    "ActivityCompleted",
    "ActivityDuration",
    "BuiltNestCount",
    "BuiltWrongNestCount",
    "EatFishCount",
    "EggLostCount",
    "EggRecoverTime",
    "GazeCount",
    "GazeDuration",
    "LogVersion",
    "MirrorWaddleDuration",
    "PenguinInteractCount",
    "PlayerInactiveAvgDuration",
    "RegionDuration",
    "RegionEnterCount",
    "RegionsEncountered",
    "RingChimesCount",
    "RockBashCount",
    "RockMultiplePickupCount",
    "RockPickupCount",
    "SessionDuration",
    "SkuaBashCount",
    "SkuaPeckCount",
    "SnowBallDuration",
    "WaddleCount",
    "WaddlePerRegion",
    "WaddlePerRegion"
]
# aggregated features

from . import BuiltNestCount
from . import BuiltWrongNestCount
from . import EatFishCount
from . import EggLostCount
from . import EggRecoverTime
from . import GazeCount
from . import GazeDuration
from . import LogVersion
from . import MirrorWaddleDuration
from . import PenguinInteractCount
from . import PlayerInactiveAvgDuration
from . import RegionsEncountered
from . import RingChimesCount
from . import RockBashCount
from . import RockMultiplePickupCount
from . import RockPickupCount
from . import SessionDuration
from . import SkuaBashCount
from . import SkuaPeckCount
from . import SnowBallDuration
from . import WaddleCount

# percount features
from . import ActivityCompleted
from . import ActivityDuration
from . import RegionDuration
from . import RegionEnterCount
from . import WaddlePerRegion
