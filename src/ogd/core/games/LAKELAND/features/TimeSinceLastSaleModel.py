from typing import List, Optional, Dict, Any
from models.SequenceModel import SequenceModel
import datetime

## @class TimeSinceLastSaleModel
# Returns the number of seconds since the last purchase a player made
# Rationale: This seems like the simplest and easiest to interpret measure of whether a player
# is stagnating by not selling anything.
# @param levels: Levels applicable for model

class TimeSinceLastSaleModel(SequenceModel):
    def __init__(self, levels: List[int] = []):
        '''
        @class TimeSinceLastSaleModel
        Returns the number of seconds since the last purchase a player made
        :param levels: Levels applicable for model
        '''
        super().__init__()

    def _eval(self, events: List[Dict[str, Any]], verbose: bool = False) -> Optional[int]:
        assert events
        now = events[-1]["client_time"]
        for event in reversed(events):
            if event["event_custom"] == 37:
                event_time = event["client_time"]
                if type(event_time) is str:
                    event_time = datetime.datetime.fromisoformat(event_time)
                if type(now) is str:
                    now = datetime.datetime.fromisoformat(now)
                return (now - event_time).seconds
        return None


    def __repr__(self):
        return f"TimeSinceLastSaleModel(levels={self._levels}, input_type={self._input_type})"