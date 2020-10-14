from typing import List, Optional, Dict, Any
from models.SequenceModel import SequenceModel

# birth/death events
# "BUY" = 7
# ["HOME", "FARM", "LIVESTOCK"] = [1,3,5]

## @class TownCompositionModel
# Returns a list with the number of homes, farms, and dairy farms (in that order)
# Rationale: This is a quick and easy way to see the current town composition.
# @param levels: Levels applicable for model
class TownCompositionModel(SequenceModel):
    def __init__(self, levels: List[int] = []):
        '''
        @class TownCompositionModel
        Returns a list with the number of homes, farms, and dairy farms (in that order)
        :param levels: Levels applicable for model
        '''
        super().__init__()

    def _eval(self, events: List[Dict[str, Any]], verbose: bool = False) -> List[int]:
        assert events
        homes = 0
        farms = 0
        dairy = 0
        for event in reversed(events):
            # gamestate
            if event["event_custom"] == 0:
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
        return [homes, farms, dairy]

    # reformat raw variable functions
    def _read_stringified_array(self, arr: str) -> List[int]:
        if not arr:
            return []
        return [int(x) for x in arr.split(',')]


    def _array_to_mat(self, num_columns: int, arr: List[int]) -> List[List[int]]:
        assert len(arr) % num_columns == 0
        return [arr[i:i + num_columns] for i in range(0, len(arr), num_columns)]


def __repr__(self):
        return f"TownCompositionModel(levels={self._levels}, input_type={self._input_type})"