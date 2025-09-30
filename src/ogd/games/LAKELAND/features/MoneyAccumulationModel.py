from typing import List, Optional, Dict, Any
from models.SequenceModel import SequenceModel

## @class MoneyAccumulationModel
# Returns a list with (1) the current amount of money and (2) the total number of homes,
# farms, and dairy farms
# Rationale: These two values give a simple-to-interpret snapshot of how much money someone is
# hanging onto compared to how well-developed their town is. If money is high, but the town is
# small, it could represent indecision in the player.
# @param levels: Levels applicable for model
class MoneyAccumulationModel(SequenceModel):
    def __init__(self, levels: List[int] = []):
        '''
        @class MoneyAccumulationModel
        Returns a list with (1) the current amount of money and (2) the total number of homes,
        farms, and dairy farms
        :param levels: Levels applicable for model
        '''
        super().__init__()

    def _eval(self, events: List[Dict[str, Any]], verbose: bool = False) -> List[int]:
        assert events
        homes = 0
        farms = 0
        dairy = 0
        money = 0
        money_since_gamestate = 0
        for event in reversed(events):
            # tally money for selling stuff since most recent gamestate event
            if event["event_custom"] == 37:
                money_since_gamestate += event["event_data_complex"]["worth"]
            # get tallies from most recent gamestate event
            if event["event_custom"] == 0:
                money = event["event_data_complex"]["money"]
                tile_string = event["event_data_complex"]["tiles"]
                _tile = self._read_stringified_array(tile_string)
                tile = self._array_to_mat(4, _tile)
                for i in range(0, len(tile)):
                    if tile[i][3] == 8:
                        homes += 1
                    elif tile[i][3] == 9:
                        farms += 1
                    elif tile[i][3] == 10:
                        dairy += 1
                break
        return [money + money_since_gamestate, homes + farms + dairy]

    # reformat raw variable functions
    def _read_stringified_array(self, arr: str) -> List[int]:
        if not arr:
            return []
        return [int(x) for x in arr.split(',')]


    def _array_to_mat(self, num_columns: int, arr: List[int]) -> List[List[int]]:
        assert len(arr) % num_columns == 0
        return [arr[i:i + num_columns] for i in range(0, len(arr), num_columns)]


def __repr__(self):
        return f"MoneyAccumulationModel(levels={self._levels}, input_type={self._input_type})"