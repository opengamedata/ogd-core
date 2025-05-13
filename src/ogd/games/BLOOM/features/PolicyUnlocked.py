from collections import Counter
from typing import Any, List

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

class PolicyUnlocked(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.policies_unlocked = Counter()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["policy_unlocked"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        _policy = event.EventData.get("policy_name")
        if _policy:
            self.policies_unlocked[_policy.upper()] += 1

    def _updateFromFeatureData(self, feature: FeatureData) -> None:
        return

    def _getFeatureValues(self) -> List[Any]:
        ret_val : List[Any]

        
        ret_val = [
            self.policies_unlocked.total(),
            self.policies_unlocked["SALESTAXPOLICY"]  > 0, max(self.policies_unlocked["SALESTAXPOLICY"]  - 1, 0),
            self.policies_unlocked["IMPORTTAXPOLICY"] > 0, max(self.policies_unlocked["IMPORTTAXPOLICY"] - 1, 0),
            self.policies_unlocked["RUNOFFPOLICY"]    > 0, max(self.policies_unlocked["RUNOFFPOLICY"]    - 1, 0),
            self.policies_unlocked["SKIMMINGPOLICY"]  > 0, max(self.policies_unlocked["SKIMMINGPOLICY"]  - 1, 0),
        ]

        return ret_val

    def BaseFeatureSuffix(self) -> str:
        return "Count"

    def Subfeatures(self) -> List[str]:
        return ["SalesTax", "SalesTax-Repeats", "ImportTax", "ImportTax-Repeats", "Runoff", "Runoff-Repeats", "Skimming", "Skimming-Repeats"]