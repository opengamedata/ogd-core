# import libraries
import logging
from datetime import timedelta
from typing import Any, List, Optional
# import locals
from utils import Logger
from games.AQUALAB.features.PerJobFeature import PerJobFeature
from schemas.FeatureData import FeatureData
from schemas.Event import Event

class JobActiveTime(PerJobFeature):

    def __init__(self, name:str, description:str, job_num:int, job_map:dict):
        super().__init__(name=name, description=description, job_num=job_num, job_map=job_map)
        self._job_start_time = None
        self._prev_timestamp = None
        self._time = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["accept_job", "switch_job", "complete_job"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if self._job_start_time:
            self._time += (self._prev_timestamp - self._job_start_time).total_seconds()
            self._job_start_time = event.timestamp

        if event.user_id == "MordantDead":
            Logger.Log(f"Processing event {event}", logging.WARNING)
        if event.event_name == "accept_job":
            self._job_start_time = event.timestamp
        elif event.event_name == "switch_job":
            self._
        elif event.event_name == "complete_job":
            if self._job_start_time:
                self._time += (event.timestamp - self._job_start_time).total_seconds()
                self._job_start_time = None
            else:
                Logger.Log(f"{event.user_id} ({event.session_id}) completed job {event.event_data['job_name']['string_value']} with no active start time!", logging.WARNING)

        self._prev_timestamp = event.timestamp

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [timedelta(seconds=self._time)]

    # *** Optionally override public functions. ***
    def MinVersion(self) -> Optional[str]:
        return "1"
