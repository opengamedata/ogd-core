from typing import List, Optional, Dict, Any
from models.SequenceModel import SequenceModel
import datetime


## @class RecentPurchasesModel
# Returns a list of 8 lists, corresponding to the 8 items that can be purchased: (in this order) [homes, food,
# farms, fertilizer, livestock, skimmers, signs, roads].
# In each list is the number of seconds since that item was purchased, for each time it was purchased within the
# 10 most recent purchases.
# Rationale: This gives us options for displaying the data however we feel is most helpful. For example, we could
# just indicate the length of each list to indicate the number of purchases of each type within the last ten overall
# purchases, or we could incorporate the time stamps as well.
# @param levels: Levels applicable for model
class RecentPurchasesModel(SequenceModel):
    def __init__(self, levels: List[int] = []):
        '''
        @class RecentPurchasesModel
        Returns a list of 8 lists, corresponding to the 8 items that can be purchased: (in this order) [homes, food,
        farms, fertilizer, livestock, skimmers, signs, roads].
        In each list is the number of seconds since that item was purchased, for each time it was purchased within the
        10 most recent purchases.
        :param levels: Levels applicable for model
        '''
        super().__init__()

    def _eval(self, events: List[Dict[str, Any]], verbose: bool = False) -> List[List[int]]:
        assert events
        homes = []
        food = []
        farms = []
        fertilizer = []
        livestock = []
        skimmers = []
        signs = []
        roads = []
        count = 0
        now = events[-1]["client_time"]
        if type(now) is str:
            now = datetime.datetime.fromisoformat(now)
        for event in reversed(events):
            # gamestate
            if event["event_custom"] == 7 and event["event_data_complex"]["success"]:
                if event["event_data_complex"]["buy"] == 1:
                    event_time = event["client_time"]
                    if type(event_time) is str:
                        event_time = datetime.datetime.fromisoformat(event_time)
                    homes.append((now - event_time).total_seconds())
                elif event ["event_data_complex"]["buy"] == 2:
                    event_time = event["client_time"]
                    if type(event_time) is str:
                        event_time = datetime.datetime.fromisoformat(event_time)
                    food.append((now - event_time).total_seconds())
                elif event["event_data_complex"]["buy"] == 3:
                    event_time = event["client_time"]
                    if type(event_time) is str:
                        event_time = datetime.datetime.fromisoformat(event_time)
                    farms.append((now - event_time).total_seconds())
                elif event["event_data_complex"]["buy"] == 4:
                    event_time = event["client_time"]
                    if type(event_time) is str:
                        event_time = datetime.datetime.fromisoformat(event_time)
                    fertilizer.append((now - event_time).total_seconds())
                elif event["event_data_complex"]["buy"] == 5:
                    event_time = event["client_time"]
                    if type(event_time) is str:
                        event_time = datetime.datetime.fromisoformat(event_time)
                    livestock.append((now - event_time).total_seconds())
                elif event["event_data_complex"]["buy"] == 6:
                    event_time = event["client_time"]
                    if type(event_time) is str:
                        event_time = datetime.datetime.fromisoformat(event_time)
                    skimmers.append((now - event_time).total_seconds())
                elif event["event_data_complex"]["buy"] == 7:
                    event_time = event["client_time"]
                    if type(event_time) is str:
                        event_time = datetime.datetime.fromisoformat(event_time)
                    signs.append((now - event_time).total_seconds())
                elif event["event_data_complex"]["buy"] == 8:
                    event_time = event["client_time"]
                    if type(event_time) is str:
                        event_time = datetime.datetime.fromisoformat(event_time)
                    roads.append((now - event_time).total_seconds())
                # Check if ten purchases have been tallied. If so, break from the loop.
                count += 1
                if count >= 10:
                    break
        return [homes, food, farms, fertilizer, livestock, skimmers, signs, roads]



def __repr__(self):
        return f"RecentPurchasesModel(levels={self._levels}, input_type={self._input_type})"