# import libraries
from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

# import PerCountyFeature
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.games.BLOOM.features.PerCountyFeature import PerCountyFeature

class CountyLatestMoney(PerCountyFeature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.latest_money: Dict[str, Optional[int]] = {county: None for county in self.COUNTY_LIST}

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["switch_county"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _validateEventCountIndex(self, event: Event):
        ret_val: bool = False

        county_name = event.EventData.get('county_name', "COUNTY NAME NOT FOUND")
        if county_name is not None:
            if county_name in self._county_map and self._county_map[county_name] == self.CountIndex:
                ret_val = True
        else:
            self.WarningMessage(f"Got invalid county_name data in {type(self).__name__}")

        return ret_val

    def _updateFromEvent(self, event: Event) -> None:
        county_name = event.EventData.get("county_name", None)
        current_money = event.GameState.get("current_money", None)
        if county_name and current_money is not None and county_name in self.latest_money:
            self.latest_money[county_name] = current_money

    def _updateFromFeatureData(self, feature: FeatureData):
        pass

    def _getFeatureValues(self) -> List[Any]:
        return [self.latest_money]

    def Subfeatures(self) -> List[str]:
        return []
