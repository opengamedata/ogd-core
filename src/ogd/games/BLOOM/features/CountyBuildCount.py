"""# import libraries
from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class CountyBuildCount(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.build_counts: Dict[str, int] = {}

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["execute_build_queue"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        county_name = event.EventData.get("county_name", None)
        if county_name:
            if county_name not in self.build_counts:
                self.build_counts[county_name] = 1
            else:
                self.build_counts[county_name] += 1

    def _updateFromFeatureData(self, feature: FeatureData):
        pass

    def _getFeatureValues(self) -> List[Any]:
        return [self.build_counts]

    def Subfeatures(self) -> List[str]:
        return []
"""

# import libraries
from typing import Any, Dict, List
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

# import PerCountyFeature
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature

class PerCountyBuildCount(PerCountyFeature):
    def __init__(self, params: GeneratorParameters, county_map: Dict[str, int]):
        super().__init__(params=params, county_map=county_map)
        self.build_counts: Dict[str, Dict[str, int]] = {county: 0 for county in county_map.keys()}

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["execute_build_queue"]

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
        if county_name and county_name in self.build_counts:
            self.build_counts[county_name] += 1

    def _updateFromFeatureData(self, feature: FeatureData):
        pass

    def _getFeatureValues(self) -> List[Any]:
        return [self.build_counts]

    def Subfeatures(self) -> List[str]:
        return []
