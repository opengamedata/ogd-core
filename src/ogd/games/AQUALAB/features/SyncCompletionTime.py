# import libraries
import logging
from datetime import datetime, timedelta
from typing import Any, List, Optional
# import locals
from ogd.core.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class SyncCompletionTime(Feature):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._session_id = None
        self._sim_start_time : Optional[datetime] = None
        self._prev_timestamp : Optional[datetime] = None
        self._time = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["begin_simulation, simulation_sync_achieved"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []
    def _updateFromEvent(self, event:Event) -> None:
        if event.SessionID != self._session_id:
            _prev_id = self._session_id
            self._session_id = event.SessionID
            if self._sim_start_time is not None and self._prev_timestamp is not None:
                self._time += (self._prev_timestamp - self._sim_start_time).total_seconds()
                self._sim_start_time = event.Timestamp
            # if previous ID wasn't None, then this isn't the first session we've seen,
            # so we warn user that previous session left us without one of the things.
            elif _prev_id is not None:
                Logger.Log(f"In SyncCompletionTime, got a new session but either missing sim_start_time or prev_timestamp!", logging.WARN)

        if event.EventName == "begin_simulation":
            self._sim_start_time = event.Timestamp
        elif event.EventName == "simulation_sync_achieved":
            if self._sim_start_time is not None:
                self._time += (event.Timestamp - self._sim_start_time).total_seconds()
                self._sim_start_time = None
            else:
                self.WarningMessage("Simulation synced when we had no active start time!")

        self._prev_timestamp = event.Timestamp

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [timedelta(seconds=self._time)]

    # *** Optionally override public functions. ***
