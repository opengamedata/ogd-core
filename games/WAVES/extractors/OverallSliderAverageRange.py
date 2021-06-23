import typing
from GameTable import GameTable
from WaveFeature import WaveFeature

class TotalSliderMoves(WaveFeature):
    def __init__(self, game_table: GameTable, accepted_events: typing.List[str], min_data_version:int=-math.inf, max_data_version:int=math.inf):
        WaveFeature.__init__(self, game_table, accepted_events, min_data_version, max_data_version)
        self._count = 0

    def CalculateFinalValues(self) -> typing.Tuple:
        return (None)

    def _extractFromRow(self, row: typing.List):
