import logging
from typing import Any, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature
from ogd.common.utils.Logger import Logger

class SurveyItemResponse(PerCountFeature):
    def __init__(self, params: GeneratorParameters, target_survey:str, retest:bool=False):
        self._target_survey = target_survey
        self._response = None
        self._prompt = None
        self._response_count = 0
        self._retest = retest
        self._retest_response = None
        super().__init__(params=params)

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["survey_submitted"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _validateEventCountIndex(self, event: Event) -> bool:
        """SurveyItemResponse implementation of event validation against CountIndex.

        This is a slight abuse of the function, as we're ignoring the actual CountIndex here.
        Really, just validating the event against a target.
        Basic idea is, this feature is operating on events that encode a collection of items, namely responses.
        Thus, rather than looking for an event that has a single item to match against the Extractor instance's
        index, we're looking for the event that will contain the item matching CountIndex.
        The rest of the Extractor's logic will handle retrieval of the response from the collection.

        :param event: The event to be validated
        :type event: Event
        :return: True if the event was for the survey whose name is indicated as the target survey, otherwise False
        :rtype: bool
        """
        survey_name = event.EventData.get("display_event_id", None)
        
        if not survey_name:
            Logger.Log(f"Missing display_event_id in survey event, for player {event.UserID}, session {event.SessionID}", level=logging.WARNING)
            return False
            
        return survey_name == self._target_survey

    def _updateFromEvent(self, event: Event) -> None:
        self._response_count += 1

        _responses = event.EventData.get("responses", {})
        if len(_responses) > self.CountIndex:
            self._prompt = _responses[self.CountIndex].get("prompt", None)
            # If it was the first time they got the survey, 
            if self._response_count == 1:
                self._response = _responses[self.CountIndex].get("response", None)
            elif self._retest:
                self._retest_response = _responses[self.CountIndex].get("response", None)
            else:
                if self.ExtractMode != ExtractionMode.POPULATION:
                    Logger.Log(f"SurveyItemResponse feature for {self._target_survey} had an unexpected retest, for player {event.UserID}, session {event.SessionID}!", logging.WARN)
                    self._response = _responses[self.CountIndex].get("response", None)
        else:
            Logger.Log(f"SurveyItemResponse feature for {self._target_survey} got a survey_submitted event with fewer than {self.CountIndex} items, for player {event.UserID}, session {event.SessionID}!", logging.WARN)

    def _updateFromFeature(self, feature: Feature):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._response, self._retest_response, self._prompt, self._response_count]

    def Subfeatures(self) -> List[str]:
        return ["Retest", "Prompt", "Count"]

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.SESSION, ExtractionMode.PLAYER]

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"




