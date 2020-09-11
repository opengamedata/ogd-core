from typing import List, Optional, Dict, Any
import logging
import datetime

from models.SequenceModel import SequenceModel
from feature_extractors.LakelandExtractor import  LakelandExtractor

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
        start_time = datetime.datetime.fromisoformat(events[0]["client_time"])
        skip = True
        assert events
        population = 0
        for event in events:
            # If the event is a newfarmbit, add 1 to population.
            # If the event is a farmbitdeath, subtract 1 from the population.
            event_custom = event["event_custom"]
            event_str = LakelandExtractor._ENUM_TO_STR['EVENT CATEGORIES'][event_custom]
            if event_str not in ["emote"]:
                cur_time = datetime.datetime.fromisoformat(event["client_time"])
                if event_str == "buy" and event["event_data_complex"]["success"]:
                    buy_str = LakelandExtractor._ENUM_TO_STR['BUYS'][event["event_data_complex"]["buy"]].upper()
                    event_str = f'{event_str} {buy_str}'
                if event_str == 'startgame':
                    debug_str = "START" if not event["event_data_complex"].get("continue") else "CONTINUE"
                    debug_str += f' Language: {event["event_data_complex"].get("language")}'
                    event_str = f'{event_str} {debug_str}'
                logging.debug(f"{population:<3} {event_str:<20} {cur_time-start_time}")
            if skip:
                if event_custom not in [1, 31]: # newgames start with STARTGAME; continues start with NEWFARMBIT
                    continue
                else:
                    population = 0
                    skip = False
            if event_custom == 31: # newfarmbit
                population += 1
            elif event_custom == 18: # death
                population = population - 1
                assert population >= 0, "Population became negative"
            elif event_custom in [40,23]: # reset / endgame
                skip = True
        return population


    def __repr__(self):
        return f"PopulationModel(levels={self._levels}, input_type={self._input_type})"
