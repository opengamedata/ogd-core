from typing import Any, List

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class JobsCompleted(SessionFeature):

    def __init__(self, params:GeneratorParameters, player_id:str):
        self._player_id = player_id
        super().__init__(params=params)
        self._jobs_completed = []

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["complete_job"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        if event.UserID == self._player_id:
            _job_name = event.GameState.get('job_name', event.EventData.get('job_name', "JOB NAME NOT FOUND"))
            if event.app_version == 'Aqualab' or event.app_version == 'None':
                self._jobs_completed.append(_job_name.get('string_value'))
            else:
                self._jobs_completed.append(_job_name)

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [len(self._jobs_completed), self._jobs_completed]

    # *** Optionally override public functions. ***

    def Subfeatures(self) -> List[str]:
        return ["Names"]
