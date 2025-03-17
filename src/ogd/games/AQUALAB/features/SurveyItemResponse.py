import logging
from typing import Any, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from ogd.common.utils.Logger import Logger

class SurveyItemResponse(PerCountFeature):
    def __init__(self, params: GeneratorParameters, target_survey:str):
        super().__init__(params=params)
        self._target_survey = target_survey
        self._response = None
        self._prompt = None
        self._response_count = 0

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
            Logger.Log("Missing display_event_id in survey event", level=logging.WARNING)
            return False
            
        return survey_name == self._target_survey

    def _updateFromEvent(self, event: Event) -> None:
        _responses = event.EventData.get("responses", {})
        if len(_responses) > self.CountIndex:
            self._response = _responses[self.CountIndex].get("response", None)
            self._prompt = _responses[self.CountIndex].get("prompt", None)
            if self._response:
                self._response_count += 1
            else:
                Logger.Log(f"SurveyItemResponse feature for {self._target_survey} did not get a response value for the response at index {self.CountIndex}!", logging.WARN)
        else:
            Logger.Log(f"SurveyItemResponse feature for {self._target_survey} got a survey_submitted event with fewer than {self.CountIndex} items!", logging.WARN)

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._response, self._prompt, self._response_count]

    def Subfeatures(self) -> List[str]:
        return ["Prompt", "Count"]

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"




