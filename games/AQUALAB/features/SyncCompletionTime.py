# global imports
import logging
from typing import Any, List
# local imports
import utils
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class SyncCompletionTime(Feature):

    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0)
        self._sim_start_time = None
        self._time = None

    # *** Implement abstract functions ***
    def _getEventDependencies(self) -> List[str]:
        return ["begin_simulation, simulation_sync_achieved"]

    def _getFeatureDependencies(self) -> List[str]:
        return []
    def _extractFromEvent(self, event:Event) -> None:
        if event.event_name == "begin_simulation":
            self._sim_start_time = event.timestamp
        elif event.event_name == "simulation_sync_achieved":
            if self._sim_start_time is not None:
                self._time = event.timestamp - self._sim_start_time
            else:
                utils.Logger.Log("Simulation synced when we had no active start time!", logging.WARNING)

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._time]

    # *** Optionally override public functions. ***
