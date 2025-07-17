from collections import Counter
from typing import Any, List, Optional

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from collections import defaultdict


class TopJobCompletionDestinations(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)

        # county_list = ["Hillside","Forest", "Prairie", "Wetland", "Urban"]
        
        # if self.CountIndex is not None:
        #     self.county_index = self.CountIndex
        #     self.county_name = county_list[self.CountIndex]
        # else:
        #     raise ValueError("JobsAttempted was not given a count index!")
        
        self.last_unlocked_county = {} 
        self.county_completion_pairs = defaultdict(lambda: defaultdict(list)) 

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["game_start","county_unlocked"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        player_id = event.user_id
        event_name = event.EventName
        
        if event_name == "game_start" and self.last_unlocked_county[player_id] == None:
            # print("vent:", event)
            # print("data :",event.EventData)
            # county_name = event.EventData.get("county_name")
            # if county_name == "Hillside":
            self.last_unlocked_county[player_id] = "Hillside"
            print(f"Game started for player {player_id}, setting last unlocked county to Hillside")

        # elif event_name == "county_unlocked":
        #     current_county = event.EventData.get("county_name")
        #     last_county = self.last_unlocked_county.get(player_id, None)
        #     if last_county and last_county != current_county:
        #         if player_id not in self.county_completion_pairs[last_county][current_county]:
        #             self.county_completion_pairs[last_county][current_county].append(player_id)

        #     self.last_unlocked_county[player_id] = current_county


        # print(f"Processing event: {event}")
        # player_id = event.user_id

        # current_county = event.EventData.get("county_name")
        # last_county = self.last_unlocked_county.get(player_id)

        # if last_county and last_county != current_county:
        #     if player_id not in self.county_completion_pairs[last_county][current_county]:
        #         self.county_completion_pairs[last_county][current_county].append(player_id)

        # self.last_unlocked_county[player_id] = current_county

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        # print("County completion pairs:", dict(self.county_completion_pairs))
        ret_val = {}
        for src, dests in self.county_completion_pairs.items():
            sorted_dests = sorted(
                dests.items(),
                key=lambda item: len(item[1]),
                reverse=True
            )
            ret_val[src] = {item[0]: item[1] for item in sorted_dests[:5]}
        return [ret_val]
    

    def Subfeatures(self) -> List[str]:
        return []

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
