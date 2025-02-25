from typing import List, Optional, Dict, Any
import pandas as pd
from models.SequenceModel import SequenceModel

FB_DEATH_ENUM = 18

## @class DeathCountModel
# Returns the number of deaths in the game
# @param levels: Levels applicable for model
class DeathCountModel(SequenceModel):

    def __init__(self, levels=[]):
        super().__init__()

    def _eval(self, events: List[Dict[str, Any]], verbose: bool = False) -> List[int]:
        assert events
        dh_cnt = 0
        for row in events:
            if row['event_custom'] == FB_DEATH_ENUM:
                dh_cnt += 1
        return dh_cnt
