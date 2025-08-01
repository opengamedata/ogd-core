# import libraries
from typing import Any, List, Optional
# import locals
from ogd.common.utils.Logger import Logger
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature

class TotalJobRecommendationReceived(SessionFeature):

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self.recommendation_received = 0
        self.specific_recommendation_received = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["recommended_job"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        recommended_job_name = event.EventData.get("recommended_job_name")
        self.recommendation_received += 1
        if recommended_job_name != "":
            self.specific_recommendation_received += 1

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self.recommendation_received, self.specific_recommendation_received]

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"

    def Subfeatures(self) -> List[str]:
        return ["SpecificRecommendations"]
