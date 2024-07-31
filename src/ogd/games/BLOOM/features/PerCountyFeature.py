# import libraries
import logging
from typing import Optional, List
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.core.models.Event import Event

class PerCountyFeature(PerCountFeature):
    COUNTY_LIST = ["Hillside", "Forest", "Prairie", "Wetland", "Urban"]

    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _validateEventCountIndex(self, event: Event):
        ret_val: bool = False

        county_name = event.GameState.get('current_county', event.EventData.get('current_county', "COUNTY NAME NOT FOUND"))
        if county_name != "COUNTY NAME NOT FOUND":
            try:
                if self.COUNTY_LIST.index(county_name) == self.CountIndex:
                    ret_val = True
            except ValueError:
                self.WarningMessage(f"County name {county_name} not found in COUNTY_LIST in {type(self).__name__}, for event {event.EventName} with game state {event.GameState}")
        else:
            self.WarningMessage(f"Got invalid current_county name {county_name} for event {event.EventName} in {type(self).__name__}")

        return ret_val