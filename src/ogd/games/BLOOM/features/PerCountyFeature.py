# import libraries
# import locals
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.common.models.Event import Event

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
                self.WarningMessage(f"County name {county_name} not found in COUNTY_LIST ({self.COUNTY_LIST}) in {type(self).__name__}, for event {event.EventName}")
        else:
            self.WarningMessage(f"In {type(self).__name__}, for event {event.EventName}, log_version={event.LogVersion}, with game state={event.GameState} no current_county found.")

        return ret_val