from typing import List, Optional, Dict, Any
from models.SequenceModel import SequenceModel

# birth/death events
# "BUY" = 7
# ["HOME", "FARM", "LIVESTOCK"] = [1,3,5]

## @class TownCompositionModel
# Returns a tuple with (1) the total number of farms and (2) the length of the longest consecutive diagonal of farms
# @param levels: Levels applicable for model
class DiagonalFarmDetectorModel(SequenceModel):
    def __init__(self, levels: List[int] = []):
        '''
        @class TownCompositionModel
        Returns a tuple with (1) the total number of farms and (2) the length of the longest consecutive
        diagonal of farms
        :param levels: Levels applicable for model
        '''
        super().__init__()

    def _eval(self, events: List[Dict[str, Any]], verbose: bool = False) -> List[int]:
        assert events
        farmcount = 0
        diagonals = []
        for event in events:
            # gamestate
            if event["event_custom"] == 0:
                farmcount = 0
                diagonals = []
                tile_string = event["event_data_complex"]["tiles"]
                _tile = self._read_stringified_array(tile_string)
                tile = self._array_to_mat(4, _tile)
                for i in range(0, len(tile)):
                    if tile[i][3] == 9:
                        farmcount += 1
                        diagonals.append(self._right_diagonal(i, tile))
                        diagonals.append(self._left_diagonal(i, tile))
        if diagonals:
            biggest_diagonal = max(diagonals)
        else:
            biggest_diagonal = 0
        return [farmcount, biggest_diagonal]

    def _right_diagonal(self, index: int, tile: List[List[int]]) -> int:
        next = index + 51
        count = 1
        while next % 50 != 0:
            if tile[next][3] == 9:
                count += 1
                next += 51
            else:
                break
        return count

    def _left_diagonal(self, index: int, tile: List[List[int]]) -> int:
        next = index + 49
        count = 1
        while next % 50 != 49:
            if tile[next][3] == 9:
                count += 1
                next += 49
            else:
                break
        return count

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