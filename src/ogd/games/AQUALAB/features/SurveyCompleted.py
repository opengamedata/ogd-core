from typing import Any, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from ogd.common.utils.Logger import Logger

class SurveyCompleted(PerCountFeature):
    KNOWN_SURVEY_NAMES = [
    "demographics",
    "affective",
    "science-efficacy",
    "science-interest",
    "science-identity",
    "interest-items-hanson-2021",
    "values-1",
    "values-2",
    "values-3",
    "values-4",
    "values-5",
    "values-6",
    "values-7",
    "enjoyment"
    ]

    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self._completed = False
        self._responses = {}

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["survey_submitted"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _validateEventCountIndex(self, event: Event) -> bool:
        survey_name = event.EventData.get("display_event_id", None)
        
        if not survey_name:
            Logger.Log("Missing display_event_id in survey event", level="WARNING")
            return False
            
        try:
            expected_index = self.KNOWN_SURVEY_NAMES.index(survey_name)
        except ValueError:
            Logger.Log(f"Unrecognized survey name: {survey_name}", level="WARNING")
            return False
            
        return expected_index == self.CountIndex

    def _updateFromEvent(self, event: Event) -> None:
        self._completed = True
        self._responses = event.EventData.get("responses", {})

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._completed, self._responses]

    def Subfeatures(self) -> List[str]:
        return ["Responses"]

    def _getSubfeatureValues(self) -> List[Any]:
        return [self._responses]

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
