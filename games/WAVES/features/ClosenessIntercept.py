# import libraries
from schemas import Event
from typing import Any, List, Optional
# import locals
from extractors.features.Feature import Feature
from schemas.FeatureData import FeatureData
from extractors.Extractor import ExtractorParameters
from schemas.Event import Event

class ClosenessIntercept(Feature):
    def __init__(self, params:ExtractorParameters):
        Feature.__init__(self, params=params)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    def _getEventDependencies(self) -> List[str]:
        return []

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
    #     closenesses = self.move_closenesses_tx[lvl]['completeness']
    #     times = self.move_closenesses_tx[lvl]['t']
    #     ranges = self.move_closenesses_tx[lvl]['range']
    #     if times:
    #         try:
    #             X = [(times[i]-times[0]).seconds for i in range(len(times))]
    #         except Exception as err:
    #             Logger.Log(times[0])
    #             raise err
    #         y = closenesses
    #         if len(X) > 1:
    #             intercept, slope, r_sq = self._2D_linear_regression(X, y)
    #             r_sq = r_sq if not np.isnan(r_sq) else 0
    #         else:
    #             intercept, slope, r_sq = 0,0,0
    #         self._features.setValByIndex(feature_name='closenessIntercept', index=lvl, new_value=intercept)
    #         self._features.setValByIndex(feature_name='closenessSlope', index=lvl, new_value=slope)
    #         self._features.setValByIndex(feature_name='closenessR2', index=lvl, new_value=r_sq)
        pass

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return ["Not Implemented"]

    # *** Optionally override public functions. ***
