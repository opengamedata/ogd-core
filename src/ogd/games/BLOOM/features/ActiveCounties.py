from collections import Counter
from typing import Any, List, Optional

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature
from collections import defaultdict


class ActiveCounties(Extractor):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.last_unlocked_county = dict()  
        self.county_left_off = defaultdict(list) 
        
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

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
