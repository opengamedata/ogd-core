# import libraries
from typing import Any, List, Optional
from datetime import datetime, timedelta

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from ogd.common.utils.Logger import Logger
import logging

class PlayerProgressionJobNodes(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.nodes = {} # dict of nodes
        # self._job_names = {} # temporary storage: CountIndex -> job_name
        # self._job_active_times = {} # temporary storage: CountIndex -> active_time
        self._job_active_times = {} # temporary storage: CountIndex -> {job_name, active_time}
    
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["accept_job", "switch_job", "complete_job"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["JobName", "JobActiveTime"]

    def _updateFromEvent(self, event: Event) -> None:
        if event.EventName == "accept_job":
            self.nodes[event.GameState["job_name"]] = {
                "node_count": 1,
                "percentage_completed": 0,
                "time_spent": 0,  # Initialize to 0, will be updated from JobActiveTime features
            }
        elif event.EventName == "switch_job":
            self.nodes[event.GameState["job_name"]] = {
                "node_count": 1,
                "percentage_completed": 0,
                "time_spent": 0,  # Initialize to 0, will be updated from JobActiveTime features
            }
        elif event.EventName == "complete_job":
            self.nodes[event.GameState["job_name"]] = {
                "node_count": 1,
                "percentage_completed": 1,
                "time_spent": 0,  # Initialize to 0, will be updated from JobActiveTime features
            }
 
    def _updateFromFeatureData(self, feature: FeatureData):
        # Each iterated feature comes as a separate FeatureData object
        # Match them by FeatureType and CountIndex
        if feature.FeatureType == "JobName":
            if len(feature.FeatureValues) > 0:
                job_name = feature.FeatureValues[0]
                if feature.CountIndex not in self._job_active_times:
                    # Initialize with both keys (job_name may arrive before active_time)
                    self._job_active_times[feature.CountIndex] = {
                        "job_name": job_name,
                        "active_time": 0,  # Default to 0 until JobActiveTime arrives
                    }
                else:
                    self._job_active_times[feature.CountIndex]["job_name"] = job_name
        elif feature.FeatureType == "JobActiveTime":
            if len(feature.FeatureValues) > 0:
                active_time = feature.FeatureValues[0]
                # Log to debug why all active_time values are 0
                # if active_time > 0:
                #     Logger.Log(f"JobActiveTime_{feature.CountIndex}: {active_time} seconds", logging.INFO)
                if feature.CountIndex not in self._job_active_times:
                    # Initialize with both keys (active_time may arrive before job_name)
                    self._job_active_times[feature.CountIndex] = {
                        "job_name": None,  # Will be set when JobName arrives
                        "active_time": active_time,
                    }
                else:
                    # Use assignment (=) instead of += to avoid double-counting if ProcessFeatureData is called multiple times
                    self._job_active_times[feature.CountIndex]["active_time"] = active_time
 

    def _getFeatureValues(self) -> List[Any]:
        # Process all job active times and set them in self.nodes
        # Use assignment (=) since each CountIndex represents a unique job instance
        # and we want the final value, not accumulation across multiple calls
        for count_index, job_active_time in self._job_active_times.items():
            # Only process if we have both job_name and active_time
            job_name = job_active_time.get("job_name")
            active_time = job_active_time.get("active_time")
            
            # Only update if we have both job_name and a valid active_time value
            if job_name is not None and active_time is not None and job_name in self.nodes:
                # Set time_spent to the active_time value (active_time is in seconds as a float)
                # If multiple CountIndex entries map to the same job_name, the last one wins
                self.nodes[job_name]["time_spent"] = active_time
        
        return [{"nodes": self.nodes}]

    def Subfeatures(self) -> List[str]:
        return []

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
    
    @classmethod
    def AvailableModes(cls) -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER]