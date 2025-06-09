from typing import Any, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

class JobsBeforeSurvey(Feature):

    def __init__(self, params: GeneratorParameters, survey_ID: str):
        super().__init__(params=params)
        self.survey_ID = survey_ID
        self._job_names: List[str] = []
        self._survey_found = False

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["complete_job", "survey_submitted"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        if self._survey_found:
            return 

        if event.EventName == "complete_job":
            job_name = event.EventData.get("job_name")
            if job_name:
                self._job_names.append(job_name)
        elif event.EventName == "survey_submitted":
            survey_id = event.EventData.get("survey_id")
            if survey_id == self.survey_ID:
                self._survey_found = True

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._job_names]

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
