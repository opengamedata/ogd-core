import typing
from GameTable import GameTable
from WaveFeature import WaveFeature

class TotalSliderMoves(WaveFeature):
    def __init__(self, game_table: GameTable, accepted_events: typing.List[str], min_data_version:int=-math.inf, max_data_version:int=math.inf):
        WaveFeature.__init__(self, game_table, accepted_events, min_data_version, max_data_version)
        # create one counter of slider moves for each level.
        self._counts = [0 for i in range(game_table.min_level, game_table.max_level+1)]

    def CalculateFinalValues(self) -> typing.Tuple:
        return (None)

    def _extractFromRow(self, row: typing.List):
