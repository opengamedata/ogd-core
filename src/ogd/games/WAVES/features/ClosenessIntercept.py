# import libraries
from ogd.core.models import Event
from typing import Any, List, Optional
# import locals
from ogd.core.generators.extractors.Feature import Feature
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData


class ClosenessIntercept(Feature):
    def __init__(self, params:GeneratorParameters):
        Feature.__init__(self, params=params)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
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

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return ["Not Implemented"]

    # *** Optionally override public functions. ***
