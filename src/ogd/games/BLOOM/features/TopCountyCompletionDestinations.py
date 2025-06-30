from collections import Counter
from typing import Any, List, Optional

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from collections import defaultdict


class TopCountyCompletionDestinations(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.last_unlocked_county = {} 
        self.county_completion_pairs = defaultdict(lambda: defaultdict(list)) 

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["county_unlocked"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        # print(f"Processing event: {event}")
        player_id = event.user_id

        current_county = event.EventData.get("county_name")
        last_county = self.last_unlocked_county.get(player_id)

        if last_county and last_county != current_county:
            self.county_completion_pairs[last_county][current_county].append(player_id)

        self.last_unlocked_county[player_id] = current_county


    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
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
