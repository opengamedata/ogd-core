from typing import Any, List
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature
from ogd.games.BLOOM.detectors.AlertFollowedByInspect import AlertFollowedByInspect
from ogd.games.BLOOM.detectors.AlertFollowedByPolicy import AlertFollowedByPolicy

class AlertResponseCount(Feature):
    """Feature to indicate how often players "responded" to an alert.

    Here, "response" refers to a case where a player opened (i.e. "reviewed") an alert,
    then "responded" to what they saw by either inspecting the relevant tile from which the alert originated,
    or changing a policy in a way suggested within the alert (see `AlertFollowedByPolicy` detector for details).
    """
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.alert_response_counts = {
            combo.__str__(): 0 for combo in AlertFollowedByInspect.Inspection
        } | {
            combo.__str__(): 0 for combo in AlertFollowedByPolicy.Adjustment
        }

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["alert_followed_by_inspect", "alert_followed_by_policy"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        alert_response = event.EventData.get("player_action", None)
        if alert_response is not None:
            self.alert_response_counts[alert_response] += 1

    def _updateFromFeatureData(self, feature: FeatureData) -> None:
        return

    def _getFeatureValues(self) -> List[Any]:
        ret_val : List[Any]

        # Total good policy count
        inspect_counts = [self.alert_response_counts[str(inspect)] for inspect in AlertFollowedByInspect.Inspection]
        adjust_counts  = [self.alert_response_counts[str(adjust)] for adjust in AlertFollowedByPolicy.Adjustment]
        ret_val        = [sum(self.alert_response_counts.values())] + inspect_counts + adjust_counts

        return ret_val

    def Subfeatures(self) -> List[str]:
        return [str(inspect) for inspect in AlertFollowedByInspect.Inspection] + [str(adjustment) for adjustment in AlertFollowedByPolicy.Adjustment]