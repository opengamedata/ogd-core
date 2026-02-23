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

class PlayerProgressionLinks(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self.links = {"completed": {}, "switched": {}} # dict of links
        self.prev_job_completed = None
        self.prev_job_switched = None
    
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["switch_job", "complete_job"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        job_name = event.GameState["job_name"]

        if event.EventName == "complete_job":
            self.prev_job_completed = job_name
                
        if event.EventName == "switch_job":
            prev_job_name = event.EventData["prev_job_name"]

            if prev_job_name != "no-active-job": # true job switch
                if job_name != "no-active-job":
                    if prev_job_name not in self.links["switched"]:
                        self.links["switched"][prev_job_name] = {}
                    if job_name not in self.links["switched"][prev_job_name]:
                        self.links["switched"][prev_job_name][job_name] = 1
                    else:
                        self.links["switched"][prev_job_name][job_name] += 1
            elif self.prev_job_completed is not None: 
                if self.prev_job_completed not in self.links["completed"]:
                    self.links["completed"][self.prev_job_completed] = {}
                if job_name not in self.links["completed"][self.prev_job_completed]:
                    self.links["completed"][self.prev_job_completed][job_name] = 1
                else:
                    self.links["completed"][self.prev_job_completed][job_name] += 1
                self.prev_job_completed = None
 
    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [{"links": self.links}]

    def Subfeatures(self) -> List[str]:
        return []

    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
    
    @classmethod
    def AvailableModes(cls) -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER]