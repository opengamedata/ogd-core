# import standard libraries
import math
from datetime import timedelta
from enum import IntEnum
from typing import Callable, List, Optional

# import local files
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.detectors.DetectorEvent import DetectorEvent
from ogd.core.generators.Generator import GeneratorParameters
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.utils.Logger import Logger

class AlertFollowedByPolicy(Detector):
    class Adjustment(IntEnum):
        """An enum for the various ways a player could respond to an alert they viewed by inspecting an appropriate building.

        """
        BLOOM_INCREASE_RUNOFF = 1
        BLOOM_INCREASE_CLEANUP = 2
        SELLINGLOSS_LOWER_TAX = 3
        SELLINGLOSS_LOWER_RUNOFF = 4
        DECLININGPOP_SUBSIDIZE_MILK = 5

        def __str__(self):
            return self.name

    def __init__(self, params:GeneratorParameters, trigger_callback:Callable[[Event], None], policy_time_threshold:timedelta):
        super().__init__(params=params, trigger_callback=trigger_callback)
        self._policy_threshold = policy_time_threshold
        self._found_alert = False
        self._alert_type = "ALERT TYPE NOT FOUND!"
        self._last_alert_time = None
        self._last_alert_location = "ALERT TILE INDEX NOT FOUND!"
        self._triggered = None

    # *** Implement abstract functions ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["click_local_alert", "select_policy_card"]

    def _updateFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        time_since_alert = (event.Timestamp - self._last_alert_time) if self._last_alert_time is not None else timedelta(days=self._policy_threshold.days + 1)
        within_threshold = time_since_alert < self._policy_threshold
        old_choice_num : Optional[int | float]
        match event.EventName:
            case "click_local_alert":
                self._found_alert = True
                self._alert_type = event.EventData.get("alert_type", "ALERT TYPE NOT FOUND!")
                self._last_alert_time = event.Timestamp
                self._last_alert_location = event.EventData.get("tile_index", "ALERT TILE INDEX NOT FOUND!")
            case "select_policy_card":
                policy_type = event.EventData.get("policy", "NO POLICY TYPE FOUND!").upper()
                choice_num = event.EventData.get("choice_number")
                if self._found_alert and within_threshold:
                    match self._alert_type.upper():
                        case "BLOOM":
                            # figure out if they chose stricter policy
                            match policy_type:
                                case "RUNOFFPOLICY":
                                    old_choice_num = event.GameState.get("county_policies", {}).get("runoff", {}).get("policy_choice")
                                    old_choice_num = int(old_choice_num) if old_choice_num else math.inf
                                    if choice_num is not None and choice_num > old_choice_num:
                                        self._triggered = AlertFollowedByPolicy.Adjustment.BLOOM_INCREASE_RUNOFF
                                case "SKIMMINGPOLICY":
                                    old_choice_num = event.GameState.get("county_policies", {}).get("cleanup", {}).get("policy_choice")
                                    old_choice_num = int(old_choice_num) if old_choice_num else math.inf
                                    if choice_num is not None and choice_num > old_choice_num:
                                        self._triggered = AlertFollowedByPolicy.Adjustment.BLOOM_INCREASE_CLEANUP
                                case _:
                                    pass
                        case "SELLINGLOSS":
                            match policy_type:
                                case "SALESTAXPOLICY":
                                    old_choice_num = event.GameState.get("county_policies", {}).get("sales", {}).get("policy_choice")
                                    old_choice_num = int(old_choice_num) if old_choice_num else None
                                    # for sales tax, choice 3 is a subsidy, which is actually lowest option (player is paying out subsidy, rather than collecting a tax)
                                    # thus, need to rotate choices to make the 3 a 0, and bump all the others.
                                    old_choice_num = (int(old_choice_num) + 1) % 4 if old_choice_num else -math.inf
                                    choice_num = (choice_num + 1) % 4 if choice_num else None
                                    if choice_num is not None and choice_num < old_choice_num:
                                        self._triggered = AlertFollowedByPolicy.Adjustment.SELLINGLOSS_LOWER_TAX
                                case "RUNOFFPOLICY":
                                    old_choice_num = event.GameState.get("county_policies", {}).get("runoff", {}).get("policy_choice")
                                    old_choice_num = int(old_choice_num) if old_choice_num else -math.inf
                                    if choice_num is not None and choice_num < old_choice_num:
                                        self._triggered = AlertFollowedByPolicy.Adjustment.SELLINGLOSS_LOWER_RUNOFF
                                case _:
                                    pass
                        case "DECLININGPOP":
                            choice_name = event.EventData.get("choice_name", "NO CHOICE NAME FOUND!").upper()
                            if policy_type == "IMPORTTAXPOLICY" and choice_name == "MILK":
                                self._triggered = AlertFollowedByPolicy.Adjustment.DECLININGPOP_SUBSIDIZE_MILK
                        case _:
                            pass

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
            app_id="BLOOM", event_name="alert_followed_by_policy",
            event_data=self._triggering_event.EventData | {"player_action":str(self._triggered)}
        )
        self._triggered = None
        return ret_val
