# import libraries
from typing import Any, List, Optional
from datetime import datetime, timedelta

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

ITERATED_FEATURES = [
    "job0_JobName", "job0_JobActiveTime", "job1_JobName", "job1_JobActiveTime", "job2_JobName", "job2_JobActiveTime", "job3_JobName", "job3_JobActiveTime", "job4_JobName", "job4_JobActiveTime", 
    "job5_JobName", "job5_JobActiveTime", "job6_JobName", "job6_JobActiveTime", "job7_JobName", "job7_JobActiveTime", "job8_JobName", "job8_JobActiveTime", "job9_JobName", "job9_JobActiveTime", 
    "job10_JobName", "job10_JobActiveTime", "job11_JobName", "job11_JobActiveTime", "job12_JobName", "job12_JobActiveTime", "job13_JobName", "job13_JobActiveTime", "job14_JobName", "job14_JobActiveTime", 
    "job15_JobName", "job15_JobActiveTime", "job16_JobName", "job16_JobActiveTime", "job17_JobName", "job17_JobActiveTime", "job18_JobName", "job18_JobActiveTime", "job19_JobName", "job19_JobActiveTime", 
    "job20_JobName", "job20_JobActiveTime", "job21_JobName", "job21_JobActiveTime", "job22_JobName", "job22_JobActiveTime", "job23_JobName", "job23_JobActiveTime", "job24_JobName", "job24_JobActiveTime", 
    "job25_JobName", "job25_JobActiveTime", "job26_JobName", "job26_JobActiveTime", "job27_JobName", "job27_JobActiveTime", "job28_JobName", "job28_JobActiveTime", "job29_JobName", "job29_JobActiveTime", 
    "job30_JobName", "job30_JobActiveTime", "job31_JobName", "job31_JobActiveTime", "job32_JobName", "job32_JobActiveTime", "job33_JobName", "job33_JobActiveTime", "job34_JobName", "job34_JobActiveTime", 
    "job35_JobName", "job35_JobActiveTime", "job36_JobName", "job36_JobActiveTime", "job37_JobName", "job37_JobActiveTime", "job38_JobName", "job38_JobActiveTime", "job39_JobName", "job39_JobActiveTime", 
    "job40_JobName", "job40_JobActiveTime", "job41_JobName", "job41_JobActiveTime", "job42_JobName", "job42_JobActiveTime", "job43_JobName", "job43_JobActiveTime", "job44_JobName", "job44_JobActiveTime", 
    "job45_JobName", "job45_JobActiveTime", "job46_JobName", "job46_JobActiveTime", "job47_JobName", "job47_JobActiveTime", "job48_JobName", "job48_JobActiveTime", "job49_JobName", "job49_JobActiveTime", 
    "job50_JobName", "job50_JobActiveTime", "job51_JobName", "job51_JobActiveTime", "job52_JobName", "job52_JobActiveTime", "job53_JobName", "job53_JobActiveTime", "job54_JobName", "job54_JobActiveTime", 
    "job55_JobName", "job55_JobActiveTime", "job56_JobName", "job56_JobActiveTime", "job57_JobName", "job57_JobActiveTime", "job58_JobName", "job58_JobActiveTime", "job59_JobName", "job59_JobActiveTime", 
    "job60_JobName", "job60_JobActiveTime"
    ]

class PlayerProgressionJobNodes(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.nodes = {} # dict of nodes
        self._job_names = {} # temporary storage: CountIndex -> job_name
        self._job_active_times = {} # temporary storage: CountIndex -> active_time
    
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["accept_job", "switch_job", "complete_job"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return ITERATED_FEATURES

    def _updateFromEvent(self, event: Event) -> None:
        if event.EventName == "accept_job":
            self.nodes[event.GameState["job_name"]] = {
                "node_count": 1,
                "percentage_completed": 0,
                "time_spent": timedelta(0),
            }
        elif event.EventName == "switch_job":
            self.nodes[event.GameState["job_name"]] = {
                "node_count": 1,
                "percentage_completed": 0,
                "time_spent": timedelta(0),
            }
        elif event.EventName == "complete_job":
            self.nodes[event.GameState["job_name"]] = {
                "node_count": 1,
                "percentage_completed": 1,
                "time_spent": timedelta(0),
            }
 
    def _updateFromFeatureData(self, feature: FeatureData):
        # Each iterated feature comes as a separate FeatureData object
        # Match them by FeatureType and CountIndex
        if feature.FeatureType == "JobName":
            # Store the job name for this CountIndex
            if len(feature.FeatureValues) > 0:
                job_name = feature.FeatureValues[0]
                self._job_names[feature.CountIndex] = job_name
                # Try to match with existing active time
                if feature.CountIndex in self._job_active_times:
                    active_time = self._job_active_times[feature.CountIndex]
                    if job_name in self.nodes:
                        self.nodes[job_name]["time_spent"] += timedelta(seconds=active_time)
                    del self._job_active_times[feature.CountIndex]
        elif feature.FeatureType == "JobActiveTime":
            # Store the active time for this CountIndex
            if len(feature.FeatureValues) > 0:
                active_time = feature.FeatureValues[0]
                # Convert timedelta to seconds if needed
                if isinstance(active_time, timedelta):
                    active_time = active_time.total_seconds()
                self._job_active_times[feature.CountIndex] = active_time
                # Try to match with existing job name
                if feature.CountIndex in self._job_names:
                    job_name = self._job_names[feature.CountIndex]
                    if job_name in self.nodes:
                        self.nodes[job_name]["time_spent"] += timedelta(seconds=active_time)
                    del self._job_names[feature.CountIndex]

    def _getFeatureValues(self) -> List[Any]:
        return [{"nodes": self.nodes}]

    def Subfeatures(self) -> List[str]:
        return []

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
    
    @classmethod
    def AvailableModes(cls) -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER]