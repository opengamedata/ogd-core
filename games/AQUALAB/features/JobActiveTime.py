# import libraries
import logging
from datetime import timedelta
from typing import Any, List, Optional
# import locals
from utils import Logger
from extractors.Extractor import ExtractorParameters
from games.AQUALAB.features.PerJobFeature import PerJobFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData

class JobActiveTime(PerJobFeature):

    def __init__(self, params:ExtractorParameters, job_map:dict):
        super().__init__(params=params, job_map=job_map)
        self._total_seconds = timedelta(0)
        if self.ExportMode == ExtractionMode.USER:
            self._session_id      = None
            self._last_start_time = None
            self._last_event_time = None
        elif self.ExportMode == ExtractionMode.POPULATION:
            pass
        else:
            raise NotImplementedError(f"Got invalid export mode of {self.ExportMode.name} in JobActiveTime!")

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        if self.ExportMode == ExtractionMode.USER:
            return ["all_events"]
        else:
            return []

    def _getFeatureDependencies(self) -> List[str]:
        if self.ExportMode == ExtractionMode.POPULATION:
            return ["JobActiveTime"]
        else:
            return []

    def _extractFromEvent(self, event:Event) -> None:
        if self.ExportMode == ExtractionMode.USER:
            self._handle_user(event=event)
        elif self.ExportMode == ExtractionMode.POPULATION:
            pass

    def _extractFromFeatureData(self, feature:FeatureData):
        if self.ExportMode == ExtractionMode.USER:
            pass
        elif self.ExportMode == ExtractionMode.POPULATION:
            self._handle_population(feature=feature)

    def _getFeatureValues(self) -> List[Any]:
        return [self._total_seconds]

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

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.USER, ExtractionMode.POPULATION]

    # *** PRIVATE METHODS ***

    def _handle_user(self, event:Event) -> None:
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

    def _updateTotalTime(self):
        if self._last_start_time:
            if self._last_event_time:
                self._total_seconds += (self._last_event_time - self._last_start_time)
                self._last_start_time = None
            else:
                Logger.Log(f"JobActiveTime could not update total time, missing previous event time!", logging.WARNING)
        else:
            Logger.Log(f"JobActiveTime could not update total time for session {self._session_id}, missing start time!", logging.WARNING)

    def _handle_population(self, feature:FeatureData):
        if feature.ExportMode == ExtractionMode.USER:
            _val = feature.FeatureValues[0]
            if type(_val) == timedelta:
                self._total_seconds += _val
            else:
                Logger.Log(f"JobActiveTime for population got invalid value {_val} of type {type(_val)} for column {feature.FeatureNames[0]}", logging.WARN)
        else:
            Logger.Log(f"JobActiveTime for population got feature data for mode {feature.ExportMode.name}", logging.DEBUG)
