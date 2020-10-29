from typing import List, Optional, Dict, Any
from models.SequenceModel import SequenceModel


## @class MapSummaryModel
# Returns an array (list of lists) with values indicating the tile type for the corresponding tile in the game.
# To interpret the tile type values, see https://github.com/fielddaylab/lakeland/blob/master/README.md#TileType
# If there is at least one building present (home, farm, or dairy), the map returned is just a bounding box
# with a border width of five tiles around the area the buildings occupy.
# Otherwise, the map returned is the entire map.
# @param levels: Levels applicable for model
class MapSummaryModel(SequenceModel):
    def __init__(self, levels: List[int] = []):
        '''
        @class MapSummaryModel
        Returns an array (list of lists) with values indicating the tile type for the corresponding tile in the game.
        To interpret the tile type values, see https://github.com/fielddaylab/lakeland/blob/master/README.md#TileType
        If there is at least one building present (home, farm, or dairy), the map returned is just a bounding box
        with a border width of five tiles around the area the buildings occupy.
        Otherwise, the map returned is the entire map.
        :param levels: Levels applicable for model
        '''
        super().__init__()

    def _eval(self, events: List[Dict[str, Any]], verbose: bool = False) -> List[List[int]]:
        assert events
        # compute the full bitmap
        w, h = 50, 50;
        bitmap = [[-1 for x in range(w)] for y in range(h)]
        for event in reversed(events):
            if event["event_custom"] == 0:
                tile_string = event["event_data_complex"]["tiles"]
                _tile = self._read_stringified_array(tile_string)
                tile = self._array_to_mat(4, _tile)
                for i in range(0, len(tile)):
                    bitmap[int(i / 50)][i % 50] = tile[i][3]
                break
        # shrink the map down to only a border of five tiles around the buildings
        i_coords = []
        j_coords = []
        for i in range(50):
            for j in range(50):
                if bitmap[i][j] in [8, 9, 10]:
                    i_coords.append(i)
                    j_coords.append(j)
        if len(i_coords) != 0:
            # compute the min and max i,j coordinates, but if they are closer than five tiles
            # to the edge of the map, set them to exactly five tiles from the edge
            max_i = min([max(i_coords), 44])
            min_i = max([min(i_coords), 5])
            max_j = min([max(j_coords), 44])
            min_j = max([min(j_coords), 5])
            small_bitmap = [[bitmap[i][j] for i in range(min_i - 5, max_i + 5)] for j in range(min_j - 5, max_j + 5)]
        else:
            small_bitmap = bitmap

        return small_bitmap

    # reformat raw variable functions
    def _read_stringified_array(self, arr: str) -> List[int]:
        if not arr:
            return []
        return [int(x) for x in arr.split(',')]


    def _array_to_mat(self, num_columns: int, arr: List[int]) -> List[List[int]]:
        assert len(arr) % num_columns == 0
        return [arr[i:i + num_columns] for i in range(0, len(arr), num_columns)]


def __repr__(self):
        return f"MapSummaryModel(levels={self._levels}, input_type={self._input_type})"