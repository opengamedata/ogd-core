# Import libraries
from collections import Counter
from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from ogd.core.generators.extractors.Feature import Feature

class BuildingInspectorTabCount(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self._counter: Counter = Counter()
        self._building_type: Optional[str] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["click_inspect_building", "click_inspector_tab"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        if event.EventName == "click_inspect_building":
            # Update the building type when an inspection event occurs
            self._building_type = event.EventData.get("building_type", "UNKNOWN").upper()
        elif event.EventName == "click_inspector_tab" and self._building_type:
            # Increment the counter for the current building type on tab click
            self._counter[self._building_type] += 1

    def _updateFromFeatureData(self, feature: FeatureData):
        pass

    def _getFeatureValues(self) -> List[Any]:
        # Base feature returns the total of all counts
        total_count = sum(self._counter.values())
        city_count = self._counter.get("CITY", 0)
        dairyfarm_count = self._counter.get("DAIRYFARM", 0)
        grainfarm_count = self._counter.get("GRAINFARM", 0)
        storage_count = self._counter.get("STORAGE", 0)
        
        # Return base feature total count and subfeatures for specific buildings
        return [total_count, city_count, dairyfarm_count, grainfarm_count, storage_count]

    def Subfeatures(self) -> List[str]:
        # Subfeatures for specific building types
        return ["CityTabCount", "DairyFarmTabCount", "GrainFarmTabCount", "StorageTabCount"]
