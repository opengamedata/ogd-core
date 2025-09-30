from typing import List, Optional, Dict, Any
from models.SequenceModel import SequenceModel


## @class DiagonalFarmDetectorModel
# Returns a list with (1) the total number of farms, (2) the length of the longest consecutive diagonal
# of farms, and (3) the number of farms with at least one diagonal neighbor, but zero adjacent neighbors
# Rationale: The ratio of the first two values gives a reasonable first impression of how much the player
# is using diagonals. If the third value is high (or really, if it's much above zero), it gives very strong
# evidence the player is using the diagonal strategy.
# @param levels: Levels applicable for model
class DiagonalFarmDetectorModel(SequenceModel):
    def __init__(self, levels: List[int] = []):
        '''
        @class DiagonalFarmDetectorModel
        Returns a list with (1) the total number of farms, (2) the length of the longest consecutive
        diagonal of farms, and (3) the number of farms with at least one diagonal neighbor, but zero
        adjacent neighbors
        :param levels: Levels applicable for model
        '''
        super().__init__()

    def _eval(self, events: List[Dict[str, Any]], verbose: bool = False) -> List[int]:
        assert events
        farmcount = 0
        diagonals = []
        diagonals_only = 0
        for event in reversed(events):
            # gamestate
            if event["event_custom"] == 0:
                tile_string = event["event_data_complex"]["tiles"]
                _tile = self._read_stringified_array(tile_string)
                tile = self._array_to_mat(4, _tile)
                for i in range(0, len(tile)):
                    if tile[i][3] == 9:
                        farmcount += 1
                        diagonals.append(self._right_diagonal(i, tile))
                        diagonals.append(self._left_diagonal(i, tile))
                        if self._diagonal_neighbors_present(i, tile) and not self._adjacent_neighbors_present(i, tile):
                            diagonals_only += 1
                break
        if diagonals:
            biggest_diagonal = max(diagonals)
        else:
            biggest_diagonal = 0
        return [farmcount, biggest_diagonal, diagonals_only]

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

    def _diagonal_neighbors_present(self, index: int, tile: List[List[int]]) -> bool:
        # check all four possibilities if it's not in the first or last row
        if 49 < index < 2450:
            if index % 50 != 0:
                if tile[index + 49][3] == 9 or tile[index - 51][3] == 9:
                    return True
            if index % 50 != 49:
                if tile[index + 51][3] == 9 or tile[index - 49][3] == 9:
                    return True
        # check both possibilities if it's in the first row
        elif index <= 49:
            if index != 0:
                if tile[index + 49][3] == 9:
                    return True
            if index != 49:
                if tile[index + 51][3] == 9:
                    return True
        # check both possibilities if it's in the last row
        elif index >= 2450:
            if index % 50 != 0:
                if tile[index - 51][3] == 9:
                    return True
            if index % 50 != 49:
                if tile[index - 49][3] == 9:
                    return True
        return False

    def _adjacent_neighbors_present(self, index: int, tile: List[List[int]]) -> bool:
        if index > 49:
            if tile[index - 50][3] == 9:
                return True
        if index < 2450:
            if tile[index + 50][3] == 9:
                return True
        if index % 50 != 0:
            if tile[index - 1][3] == 9:
                return True
        if index % 50 != 49:
            if tile[index + 1][3] == 9:
                return True
        return False




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