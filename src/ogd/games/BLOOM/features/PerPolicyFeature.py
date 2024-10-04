from typing import List, Any, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode

class PerPolicyFeature(PerCountFeature):
    POLICY_LIST = ["SalesTaxPolicy", "ImportTaxPolicy", "RunoffPolicy", "SkimmingPolicy"]
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)

    def _validateEventCountIndex(self, event: Event):
        ret_val: bool = False

        policy_name = event.EventData.get('policy', event.EventData.get('policy_name', "POLICY NOT FOUND"))
        if policy_name != "POLICY NOT FOUND":
            try:
                if self.POLICY_LIST.index(policy_name) == self.CountIndex:
                    ret_val = True
            except ValueError:
                self.WarningMessage(f"Policy with name {policy_name} not found in POLICY_LIST in {type(self).__name__}, for event of type {event.EventName}")
        else:
            raise NotImplementedError(f"PerPolicyFeature subclass {type(self).__name__} requested event of type {event.EventName}, but {event.EventName} does not contain a 'policy' in its EventData.")

        return ret_val
