from typing import List, Optional, Dict, Any
from models.SequenceModel import SequenceModel


## @class RecentPurchasesModel
# Returns an 8-tuple with the number of (in this order) [homes, food, farms, fertilizer, livestock,
# skimmers, signs, roads] purchased within the last 10 purchases
# @param levels: Levels applicable for model
class RecentPurchasesModel(SequenceModel):
    def __init__(self, levels: List[int] = []):
        '''
        @class RecentPurchasesModel
        Returns an 8-tuple with the number of (in this order) [homes, food, farms, fertilizer, livestock,
        skimmers, signs, roads] purchased within the last 10 purchases
        :param levels: Levels applicable for model
        '''
        super().__init__()

    def _eval(self, events: List[Dict[str, Any]], verbose: bool = False) -> List[int]:
        assert events
        homes = 0
        food = 0
        farms = 0
        fertilizer = 0
        livestock = 0
        skimmers = 0
        signs = 0
        roads = 0
        count = 0
        for event in reversed(events):
            # gamestate
            if event["event_custom"] == 7 and event["event_data_complex"]["success"]:
                if event["event_data_complex"]["buy"] == 1:
                    homes += 1
                elif event ["event_data_complex"]["buy"] == 2:
                    food += 1
                elif event["event_data_complex"]["buy"] == 3:
                    farms += 1
                elif event["event_data_complex"]["buy"] == 4:
                    fertilizer += 1
                elif event["event_data_complex"]["buy"] == 5:
                    livestock += 1
                elif event["event_data_complex"]["buy"] == 6:
                    skimmers += 1
                elif event["event_data_complex"]["buy"] == 7:
                    signs += 1
                elif event["event_data_complex"]["buy"] == 8:
                    roads += 1
                # Check if ten purchases have been tallied. If so, break from the loop.
                count += 1
                if count >= 10:
                    break
        return [homes, food, farms, fertilizer, livestock, skimmers, signs, roads]



def __repr__(self):
        return f"RecentPurchasesModel(levels={self._levels}, input_type={self._input_type})"