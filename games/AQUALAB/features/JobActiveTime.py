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
        self._session_id      = None
        self._last_start_time = None
        self._last_event_time = None
        self._total_seconds = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["all_events"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if event.SessionID != self._session_id:
            self._session_id = event.SessionID
            # if we jumped to a new session, we only want to count time up to last event, then skip the time between sessions to new timestamp.
            self._updateTotalTime()
            self._last_start_time = event.timestamp

        if event.EventName == "accept_job":
            self._last_start_time = event.timestamp
        elif event.EventName == "switch_job":
            # if we switched into job, this becomes new start time
            if self._job_map.get(event.EventData["job_name"]['string_value'], None) == self.CountIndex:
                self._last_start_time = event.Timestamp
            # if we switched out of job, update total time in the job.
            elif self._job_map.get(event.EventData["prev_job_name"]["string_value"], None) == self.CountIndex:
                self._updateTotalTime()
        elif event.EventName == "complete_job":
            if self._last_start_time:
                self._total_seconds += (event.timestamp - self._last_start_time).total_seconds()
                self._last_start_time = None
            else:
                Logger.Log(f"{event.user_id} ({event.session_id}) completed job {event.event_data['job_name']['string_value']} with no active start time!", logging.DEBUG)

        self._last_event_time = event.timestamp

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [timedelta(seconds=self._total_seconds)]

    def _validateEventCountIndex(self, event:Event):
        ret_val : bool = False

        job_data = event.EventData["job_name"]['string_value']
        if self._job_map.get(job_data, None) is not None:
            if self._job_map.get(job_data, None) == self.CountIndex:
                    ret_val = True
            elif event.EventName == "switch_job":
                # if we got switch job, and were switching away from this instance's job, we still want to process it.
                prev_job = event.EventData["prev_job_name"]["string_value"]
                if self._job_map.get(prev_job, None) == self.CountIndex:
                    ret_val = True
        else:
            Logger.Log(f"Got invalid job_name data in {type(self).__name__}", logging.WARNING)

        return ret_val


    # *** Optionally override public functions. ***
    def MinVersion(self) -> Optional[str]:
        return "1"

    def _updateTotalTime(self):
        if self._last_start_time and self._last_event_time:
            self._total_seconds += (self._last_event_time - self._last_start_time).total_seconds()
        else:
            Logger.Log(f"Could not update total time, missing start time or event time!", logging.WARNING)
