# import libraries
from schemas import Event
from typing import Any, List, Union
# import locals
from features.FeatureData import FeatureData
from features.SessionFeature import SessionFeature
from schemas.Event import Event

class PersistentSessionID(SessionFeature):
    def __init__(self, name:str, description:str):
        SessionFeature.__init__(self, name=name, description=description)
        self._persistent_id : Union[int,None] = None

    # *** Implement abstract functions ***
    def _getEventDependencies(self) -> List[str]:
        return ["BEGIN.0"]

    def _getFeatureDependencies(self) -> List[str]:
        return []

    def _extractFromEvent(self, event:Event) -> None:
        if self._persistent_id is None:
            self._persistent_id = event.event_data['persistent_session_id']

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._persistent_id]

    # *** Optionally override public functions. ***


