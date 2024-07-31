# import libraries
import logging
from typing import Any, Dict, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.extractors.Extractor import GeneratorParameters
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class JobPriorComplete(PerCountFeature):

    def __init__(self, params:GeneratorParameters, job_map:dict):
        self._job_map = job_map
        super().__init__(params=params)
        self._prior_list = set()
        self._completed = False
        self._session_id : Optional[int] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["complete_job"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        if event.app_version == 'Aqualab' or event.app_version == 'None':
            job_data = event.GameState.get("job_name", event.EventData.get("job_name", {})).get('string_value')
        else:
            job_data = event.GameState.get("job_name", event.EventData.get("job_name", {}))
        if self._job_map[job_data] == self.CountIndex:
            self._completed = True
            return
        self._prior_list.add(self._job_map[job_data])

    def _validateEventCountIndex(self, event:Event) -> bool:
        return not self._completed

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [sorted(self._prior_list)]

    # *** Optionally override public functions. ***

    def Subfeatures(self) -> List[str]:
        return []

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
