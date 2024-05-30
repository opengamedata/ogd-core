# import libraries
from typing import Any, List, Optional
# import locals
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.models.Event import Event
from .. import Jowilder_Enumerators as je



# NOTE: Assumption is that in question 10 and qustion 16, we will have hover events which indicates new answer

class QuestionAnswers(PerCountFeature):
    def __init__(self, params: GeneratorParameters):
        PerCountFeature.__init__(self, params=params)
        self._guess_list : List[str] = []
        self.cur_question : Optional[int] = None
        self.chosen_answer : Optional[str] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _validateEventCountIndex(self, event: Event):
        if event.EventName == "CUSTOM.20":
            return self.cur_question == self.CountIndex and self.cur_question in [10, 16]
        if Event.CompareVersions(event.LogVersion, "6") >= 0 and event.EventData.get("cur_cmd_type") == 2:
                self.cur_question = je.answer_to_question(event.EventData.get("cur_cmd_fqid"), event.GameState["level"])
        return self.cur_question==self.CountIndex
    
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["CUSTOM.11", "CUSTOM.20"]
        # ["CUSTOM.11", "CUSTOM.20"] = ["wildcard_clicks", "wildcard_hover"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        # XXX: Need a new feature as dependency to become independent from wildcard_hover event. For now, it is weird that we need to seperate two kinds of events
        # NOTE: self.chosen_answer's change: None ->interacted_fqid(click and type==2) -> interacted_fqid(hover, optional step) -> none(click and type==1, that's where we update numguesses if chosen_answer is not None)
        # NOTE: self.cur_question's function: 0 -> cur_cmd_fqid&level (cmd_type==2) -> if in [10, 16] in a wildcard_hover event, update chosen answer
        if event.event_name == "CUSTOM.20" and self.chosen_answer and event.EventData.get("cur_cmd_fqid"):
            self.chosen_answer = event.EventData.get("interacted_fqid")
            return
        if Event.CompareVersions(event.LogVersion, "6") >= 0: 
            if event.EventData.get("cur_cmd_type") == 2:
                self.cur_question = je.answer_to_question(
                    event.EventData.get("cur_cmd_fqid"), event.GameState["level"])
                self.chosen_answer = event.EventData.get("interacted_fqid")
            elif event.EventData.get("cur_cmd_type") == 1:
                if self.chosen_answer:
                    self._guess_list.append(self.chosen_answer)
                    self.chosen_answer = None
        return 

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._guess_list, len(self._guess_list)]

    def Subfeatures(self) -> List[str]:
        return ["Count"]
