# import standard libraries
from enum import IntEnum
from typing import Callable, List

# import local files
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.detectors.DetectorEvent import DetectorEvent
from ogd.core.generators.Generator import GeneratorParameters
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode

class GoodPolicyCombo(Detector):
    class Combination(IntEnum):
        """An enum for the various "good combinations" of policies a player might have in their world.

        * TAX_FOR_SKIMMERS : A player has one of the skimmer policies active at the same time as a high tax
        * GOLDEN_AGE : A player with large surplus budget (surplus can be a parameter) sets tax to None or Subsidy
        * RUNOFF_BASIC : A player sets the runoff fine to Low or higher.
        * SUCCESSFUL_SUBSIDY : A player sets any of the following subsidies, by county:
            * Hillside : Milk
            * Forest : Grain
            * Prairie : Fertilizer
            * Marsh : Grain
            * Urban : Milk
        * SKIMMING_BASIC : Player sets skimming policy to Low or High in Hillside, Forest, or Marsh
        * DREDGE_BASIC : Player sets skimming policy to skim and dredge in Hillside, Forest, or Marsh
        """
        TAX_FOR_SKIMMERS = 1
        GOLDEN_AGE = 2
        RUNOFF_BASIC = 3
        HELPFUL_SUBSIDY = 4
        SKIMMING_BASIC = 5
        DREDGE_BASIC = 6

        def __str__(self):
            return self.name

    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, params:GeneratorParameters, trigger_callback:Callable[[Event], None], surplus_budget_threshold:int):
        super().__init__(params=params, trigger_callback=trigger_callback)
        self._surplus_threshold = surplus_budget_threshold
        self._triggered = None

    # *** Implement abstract functions ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["select_policy_card"]

    def _updateFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        policy = event.EventData.get("policy")
        selection = event.EvenData.get("choice_name")
        # 1. Check for skimming + high taxation combo:
        if policy == "SkimmingPolicy" and selection > 0:
            taxation = event.GameState.get("sales", {}).get("policy_choice")
            if taxation == 2:
                self._triggered = GoodPolicyCombo.Combination.TAX_FOR_SKIMMERS
        elif policy == "SalesTaxPolicy" and selection == 2:
            skimming = event.GameState.get("cleanup", {}).get("policy_choice")
            if skimming > 0:
                self._triggered = GoodPolicyCombo.Combination.TAX_FOR_SKIMMERS
        # 2. Check for relaxed taxes coinciding with large surplus of money
        elif policy == "SalesTaxPolicy" and selection in [0, 3]:
            budget = event.GameState.get("current_money")
            if budget > self._surplus_threshold:
                self._triggered = GoodPolicyCombo.Combination.GOLDEN_AGE
        # 3. Check for player using runoff policy of some kind
        elif policy == "RunoffPolicy" and selection > 0:
            self._triggered = GoodPolicyCombo.Combination.RUNOFF_BASIC
        # 4. Check for player setting a subsidy to the correct resource
        elif policy == "ImportTaxPolicy":
            county = event.GameState.get("current_county", "COUNTY_NOT_FOUND").upper()
            match selection:
                case 0 | -1:
                    # None/not set
                    pass
                case 1:
                    # Milk
                    if county in ["HILLSIDE", "URBAN"]:
                        self._triggered = GoodPolicyCombo.Combination.HELPFUL_SUBSIDY
                case 2:
                    # Grain
                    if county in ["FOREST", "MARSH"]:
                        self._triggered = GoodPolicyCombo.Combination.HELPFUL_SUBSIDY
                case 3:
                    # Fertilizer
                    if county == "PRAIRIE":
                        self._triggered = GoodPolicyCombo.Combination.HELPFUL_SUBSIDY
        # 5. Check for player using skimming or dredging in high-risk counties
        elif policy  == "SkimmingPolicy":
            county = event.GameState.get("current_county", "COUNTY_NOT_FOUND").upper()
            if county in ["HILLSIDE", "FOREST", "MARSH"]:
                if selection in [1, 2]:
                    self._triggered = GoodPolicyCombo.Combination.SKIMMING_BASIC
                if selection == 3:
                    self._triggered = GoodPolicyCombo.Combination.DREDGE_BASIC

    def _trigger_condition(self) -> bool:
        if self._triggered:
            return True
        else:
            return False

    def _trigger_event(self) -> DetectorEvent:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        # For now, include the triggering event's EventData, for better debugging.
        ret_val : DetectorEvent = self.GenerateEvent(
            app_id="BLOOM", event_name="good_policy_combo",
            event_data=self._triggering_event.EventData.update({"combination":self._triggered})
        )
        self._triggered = None
        return ret_val
