from typing import List, Optional, Dict, Any
from models.SequenceModel import SequenceModel

# birth/death events
# "BUY" = 7
# ["HOME", "FARM", "LIVESTOCK"] = [1,3,5]

## @class TownCompositionModel
# Returns a list with the number of homes, farms, and dairy farms (in that order)
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
        for event in events:
            if event["event_custom"] == 7 and event["event_data_complex"]["buy"] == 1 and \
                    event["event_data_complex"]["success"] is True:
                homes += 1
            elif event["event_custom"] == 7 and event["event_data_complex"]["buy"] == 3 and \
                    event["event_data_complex"]["success"] is True:
                farms += 1
            elif event["event_custom"] == 7 and event["event_data_complex"]["buy"] == 5 and \
                    event["event_data_complex"]["success"] is True:
                dairy += 1
        return [homes, farms, dairy]


    def __repr__(self):
        return f"TownCompositionModel(levels={self._levels}, input_type={self._input_type})"