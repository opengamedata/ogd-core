# import libraries
import json
from typing import Any, Dict, List, Optional, Type
# import local files
from generators.extractors.builtin.BuiltinExtractor import BuiltinExtractor
from generators.Generator import GeneratorParameters
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
from schemas.Event import Event

class CountEvent(BuiltinExtractor):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    _target_event = "NO EVENTS"
    def __init__(self, params:GeneratorParameters, schema_args:dict):
        self._target_event = schema_args['target_event']
        super().__init__(params=params)
        self._count = 0

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _createDerivedGenerator(cls, params:GeneratorParameters, schema_args:Dict[str,Any]) -> Type[BuiltinExtractor]:
        return type(params._name, (CountEvent,), {"_target_event" : schema_args.get("target", "NO EVENTS")})

    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return [cls._target_event]

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return []

    def _updateFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        if event.EventName == self._target_event:
            self._count += 1
        return

    def _updateFromFeatureData(self, feature: FeatureData):
        """_summary_

        :param feature: _description_
        :type feature: FeatureData
        """
        return

    def _getFeatureValues(self) -> List[Any]:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        ret_val : List[Any] = [self._count]
        return ret_val

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return [] # >>> fill in names of Subfeatures for which this Feature should extract values. <<<
    
    @staticmethod
    def MinVersion() -> Optional[str]:
        # >>> replace return statement below with a string defining the minimum logging version for events to be processed by this Feature. <<<
        return super().MinVersion()

    @staticmethod
    def MaxVersion() -> Optional[str]:
        # >>> replace return statement below with a string defining the maximum logging version for events to be processed by this Feature. <<<
        return super().MaxVersion()
