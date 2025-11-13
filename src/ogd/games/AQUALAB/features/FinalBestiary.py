import json
from typing import Any, List

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData

class FinalBestiary(SessionFeature):
    """_summary_

    :param SessionFeature: _description_
    :type SessionFeature: _type_
    """
    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._latest_bestiary = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ["switch_job"]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        _raw_bestiary = event.GameState.get("current_bestiary")
        if _raw_bestiary:
            try:
                self._latest_bestiary = json.loads(_raw_bestiary)
            except json.JSONDecodeError:
                self.WarningMessage(f"Could not load '{_raw_bestiary}' of type {type(_raw_bestiary)} as JSON!")
                self._latest_bestiary = None
        else:
            self._latest_bestiary = None

    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._latest_bestiary, len(self._latest_bestiary) if self._latest_bestiary is not None else None]

    # *** Optionally override public functions. ***

    def Subfeatures(self) -> List[str]:
        return ["Size"]

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER, ExtractionMode.SESSION]