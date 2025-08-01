from collections import Counter
from typing import Any, List, Optional

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature
from collections import defaultdict


class TopCountySwitchDestinations(Extractor):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.last_county_per_player = {}
        self.county_switch_pairs = defaultdict(lambda: defaultdict(list))

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["county_changed"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        # print(f"Processing event: {event}")
        player_id = event.user_id

        from_county = self.last_county_per_player.get(player_id)
        to_county = event.EventData.get("county_name")

        if from_county and to_county and from_county != to_county:
            if player_id not in self.county_switch_pairs[from_county][to_county]:
                self.county_switch_pairs[from_county][to_county].append(player_id)
        self.last_county_per_player[player_id] = to_county

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        ret_val = {}
        for src, dests in self.county_switch_pairs.items():
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
