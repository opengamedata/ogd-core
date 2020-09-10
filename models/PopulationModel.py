from typing import List, Optional, Dict, Any
from models.SequenceModel import SequenceModel

# birth/death events
# ["FARMBITDEATH", "NEWFARMBIT"]
# [18, 31]

## @class PopulationModel
# Returns the current population (number of living farmbits)
# @param levels: Levels applicable for model
class PopulationModel(SequenceModel):
    def __init__(self, levels: List[int] = []):
        '''
        @class PopulationModel
        Returns the current population (number of living farmbits)
        :param levels: Levels applicable for model
        '''
        super().__init__()

    def _eval(self, events: List[Dict[str, Any]], verbose: bool = False) -> int:
        assert events
        population = 0
        for event in events:
            # If the event is a newfarmbit, add 1 to population.
            # If the event is a farmbitdeath, subtract 1 from the population.
            if event["event_custom"] == 31:
                population += 1
            if event["event_custom"] == 18:
                population = population - 1
            if population < 0:
                print("Population became negative")
            if event["event_custom"] == 40:
                population = 0
        return population


    def __repr__(self):
        return f"PopulationModel(levels={self._levels}, input_type={self._input_type})"
