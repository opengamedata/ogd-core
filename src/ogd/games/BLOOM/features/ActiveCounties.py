from collections import Counter
from typing import Any, List, Optional

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from collections import defaultdict


class ActiveCounties(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.last_unlocked_county = dict()  # {player_id: county_name}
        self.county_left_off = defaultdict(list)  # {county_name: [player_id, ...]}

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["county_unlocked"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        player_id = event.user_id
        county_name = event.EventData.get("county_name")
        self.last_unlocked_county[player_id] = county_name

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        for player_id, county_name in self.last_unlocked_county.items():
            self.county_left_off[county_name].append(player_id)
        return [self.county_left_off]

    def Subfeatures(self) -> List[str]:
        return []

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
