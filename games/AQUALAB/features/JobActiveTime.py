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
            _old_sess = self._session_id
            self._session_id = event.SessionID
            # if we jumped to a new session, we only want to count time up to last event, then skip the time between sessions to new timestamp;
            # but only if we had a previous session, i.e. this isn't the first event seen.
            if _old_sess is not None:
                # Logger.Log(f"JobActiveTime attempting to update total time for {event.UserID} ({_old_sess} -> {self._session_id}) following change in session, index={event.EventSequenceIndex}", logging.INFO)
                self._updateTotalTime()
                # Logger.Log("Done", logging.INFO)
                self._last_start_time = event.timestamp
                if event.Timestamp is None:
                    Logger.Log(f"JobActiveTime received an initial event with Timestamp == None!", logging.WARN)

        if event.EventName == "accept_job":
            self._last_start_time = event.timestamp
        elif event.EventName == "switch_job":
            new_job = event.EventData["job_name"]['string_value']
            old_job = event.EventData["prev_job_name"]["string_value"]
            # if we switched into "this" job, this becomes new start time
            if self._job_map.get(new_job, None) == self.CountIndex:
                self._last_start_time = event.Timestamp
                if event.Timestamp is None:
                    Logger.Log(f"JobActiveTime received a switch_job event with Timestamp == None!", logging.WARN)
            # if we switched out of "this" job, update total time in the job.
            # note, if "this" job is no-active-job, we don't care. Further, if we switched into no-active-job, then we just completed a job and don't care.
            elif self._job_map.get(old_job, None) == self.CountIndex and new_job != "no-active-job" and old_job != "no-active-job":
                self._updateTotalTime()
        elif event.EventName == "complete_job":
            self._updateTotalTime()

        self._last_event_time = event.timestamp

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [timedelta(seconds=self._total_seconds)]

    def _validateEventCountIndex(self, event:Event):
        ret_val : bool = False

        new_job = event.EventData["job_name"]['string_value']
        if self._job_map.get(new_job, None) is not None:
            if self._job_map.get(new_job, None) == self.CountIndex:
                    ret_val = True
            elif event.EventName == "switch_job":
                # if we got switch job, and were switching away from this instance's job, we still want to process it.
                old_job = event.EventData["prev_job_name"]["string_value"]
                if self._job_map.get(old_job, None) == self.CountIndex:
                    ret_val = True
        else:
            Logger.Log(f"Got invalid job_name data in {type(self).__name__}", logging.WARNING)

        return ret_val


    # *** Optionally override public functions. ***
    def MinVersion(self) -> Optional[str]:
        return "1"

    def _updateTotalTime(self):
        if self._last_start_time:
            if self._last_event_time:
                self._total_seconds += (self._last_event_time - self._last_start_time).total_seconds()
                self._last_start_time = None
            else:
                Logger.Log(f"JobActiveTime could not update total time, missing previous event time!", logging.WARNING)
        else:
            Logger.Log(f"JobActiveTime could not update total time for session {self._session_id}, missing start time!", logging.WARNING)
