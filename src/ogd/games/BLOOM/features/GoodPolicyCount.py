from typing import Any, Dict, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from ogd.games.BLOOM.detectors.GoodPolicyCombo import GoodPolicyCombo

class GoodPolicyCount(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.good_policy_count = {
            combo.__str__(): 0 for combo in GoodPolicyCombo.Combination
        }

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["good_policy_combo"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        policy_combos = event.EventData.get("combination", None)
        if policy_combos is not None and isinstance(policy_combos, list):
            for policy in policy_combos:
                self.good_policy_count[policy] += 1

    def _updateFromFeatureData(self, feature: FeatureData) -> None:
        return

    def _getFeatureValues(self) -> List[Any]:
        # Total good policy count
        featureValues = [sum(self.good_policy_count.values())]

        # Good policy count for each combination
        for combo in GoodPolicyCombo.Combination:
            featureValues.append(self.good_policy_count[combo.__str__()])

        return featureValues

    def Subfeatures(self) -> List[str]:
        return ["TaxForSkimmers", "GoldenAge", "RunoffBasic", "HelpfulSubsidy", "SkimmingBasic", "DredgeBasic"]