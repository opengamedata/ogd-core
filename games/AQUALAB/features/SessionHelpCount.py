from typing import Any, List
# Local imports
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class SessionHelpCount(Feature):
    """_summary_

    :param Feature: _description_
    :type Feature: _type_
    """
    def __init__(self, name:str, description:str):
        super().__init__(name=name, description=description, count_index=0)
        self._count = 0

    # *** Implement abstract functions ***
    def _getEventDependencies(self) -> List[str]:
        return ["ask_for_help"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        self._count += 1

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._count]

    # *** Optionally override public functions. ***
