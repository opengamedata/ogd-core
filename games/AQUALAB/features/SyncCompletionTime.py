# import libraries
import logging
from datetime import timedelta
from typing import Any, List
# import locals
from utils import Logger
from extractors.Extractor import ExtractorParameters
from extractors.features.Feature import Feature
from schemas.FeatureData import FeatureData
from schemas.Event import Event

class SyncCompletionTime(Feature):

    def __init__(self, params:ExtractorParameters):
        super().__init__(params=params)
        self._session_id = None
        self._sim_start_time = None
        self._prev_timestamp = None
        self._time = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return ["begin_simulation, simulation_sync_achieved"]

    def _getFeatureDependencies(self) -> List[str]:
        return []
    def _extractFromEvent(self, event:Event) -> None:
        if event.SessionID != self._session_id:
            self._session_id = event.SessionID

            if self._sim_start_time:
                self._time += (self._prev_timestamp - self._sim_start_time).total_seconds()
                self._sim_start_time = event.Timestamp

        if event.EventName == "begin_simulation":
            self._sim_start_time = event.Timestamp
        elif event.EventName == "simulation_sync_achieved":
            if self._sim_start_time is not None:
                self._time += (event.Timestamp - self._sim_start_time).total_seconds()
                self._sim_start_time = None
            else:
                Logger.Log("Simulation synced when we had no active start time!", logging.WARNING)

        self._prev_timestamp = event.Timestamp

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [timedelta(seconds=self._time)]

    # *** Optionally override public functions. ***
