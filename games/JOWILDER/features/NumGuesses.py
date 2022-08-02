# import libraries
from schemas import Event
from typing import Any, List, Optional
# import locals
from schemas.FeatureData import FeatureData
from extractors.features.PerCountFeature import PerCountFeature
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event
from .. import Jowilder_Enumerators as je


class NumGuesses(PerCountFeature):
    def __init__(self, params: ExtractorParameters):
        super.__init__(self, params=params)
        # TODO: How to auto format the definition
        self._guesses_count : int = 0
        self.cur_question : int
        self.chosen_answer : int

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    # TODO: Waiting for validating countindex
    def _validateEventCountIndex(self, event: Event):
        return None
    
    def _getEventDependencies(self) -> List[str]:
        # TODO: Need to verify fromat(capital or small)
        return ["WILDCARD_CLICKS", "WILDCARD_HOVER"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event: Event) -> None:
        # TODO: Need to verify capital or small
        # XXX: Need a new feature as dependency to become independent from wildcard_hover event. For now, it is weird that we need to seperate two kinds of events
        # NOTE: self.chosen_answer's change: None ->interacted_fqid(click and type==2) -> interacted_fqid(hover, optional step) -> none(click and type==1, that's where we update numguesses if chosen_answer is not None)
        if event.event_name == "wildcard_hover" and self.cur_question in [10, 16] and self.chosen_answer and event.EventData.get("cur_cmd_fqid"):
            self.chosen_answer = event.EventData.get("interacted_fqid")
            return
        if Event.CompareVersions(event.AppVersion, "6") == 0: 
            if event.EventData.get("cur_cmd_type") == 2:
                self.cur_question = je.answer_to_question(
                    event.EventData.get("cur_cmd_fqid"), event.EventData["level"])
                self.chosen_answer = event.EventData.get("interacted_fqid")
            elif event.EventData.get("cur_cmd_type") == 1:
                if self.chosen_answer:
                    self._guesses_count += 1
                    self.chosen_answer = None
        return 

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return self._guesses_count
