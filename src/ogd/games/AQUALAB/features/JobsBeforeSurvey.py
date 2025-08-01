# Global imports
import logging
from typing import Any, List, Optional
# OGD imports
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Extractor import Extractor
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature
from ogd.common.utils.Logger import Logger

class JobsBeforeSurvey(Extractor):

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
            if not self._survey_found:
                job_name = event.EventData.get("job_name")
                if job_name:
                    self._job_names.append(job_name)
                else:
                    Logger.Log("Could not find job_name in the event data for complete_job event!", level=logging.WARNING)
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
